from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import status
from django.db import transaction
from django.conf import settings
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, PaymentVerificationSerializer

@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, context = {'request': request})
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return Response({'message': 'Product added to cart',"cart":CartSerializer(cart).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request):
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
   
    if not item_id or quantity is None:
        return Response({'error': 'Item ID and quantity are required'}, status=400)
    
    try:
        item = CartItem.objects.get(id=item_id)
        if int(quantity) < 1:
            item.delete()
            return Response({'error': 'Quantity must be at least 1'}, status=400)
        
        item.quantity = quantity
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id = request.data.get('item_id')
    CartItem.objects.filter(id=item_id).delete()
    return Response({'message': 'Item removed from cart'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    data = request.data
    phone = str(data.get('phone', '')).strip()

    if not phone.isdigit() or len(phone) < 10:
        return Response({'error': 'Invalid phone number'}, status=400)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = list(cart.items.select_related('product').all())
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=400)

    total = sum(item.product.price * item.quantity for item in cart_items)

    with transaction.atomic():
        order = Order.objects.create(user=request.user, total_amount=total)
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            for item in cart_items
        ])
        cart.items.all().delete()

    return Response(
        {'message': 'Order created successfully', 'order_id': order.id},
        status=status.HTTP_201_CREATED,
    )
  
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created successfully", "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment(request):
    try:
        import razorpay
    except ImportError:
        return Response(
            {'error': 'Razorpay is not installed. Run: pip install razorpay'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not key_id or not key_secret:
        return Response(
            {'error': 'Razorpay credentials are not configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = list(cart.items.select_related('product').all())
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    total = sum(item.product.price * item.quantity for item in cart_items)
    amount_in_paise = int(total * 100)

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        razorpay_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'cart_{cart.id}',
            'notes': {'user_id': str(request.user.id)},
        })
    except Exception:
        return Response(
            {'error': 'Unable to create payment order'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({
        'key_id': key_id,
        'payment_order_id': razorpay_order['id'],
        'amount': amount_in_paise,
        'currency': 'INR',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    serializer = PaymentVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        import razorpay
    except ImportError:
        return Response(
            {'error': 'Razorpay is not installed. Run: pip install razorpay'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not key_id or not key_secret:
        return Response(
            {'error': 'Razorpay credentials are not configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    payment_data = serializer.validated_data
    client = razorpay.Client(auth=(key_id, key_secret))
    try:
        client.utility.verify_payment_signature(payment_data)
    except razorpay.errors.SignatureVerificationError:
        return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = list(cart.items.select_related('product').all())
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    total = sum(item.product.price * item.quantity for item in cart_items)
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=Order.PaymentMethod.ONLINE,
            payment_status=Order.PaymentStatus.PAID,
            razorpay_order_id=payment_data['razorpay_order_id'],
            razorpay_payment_id=payment_data['razorpay_payment_id'],
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            for item in cart_items
        ])
        cart.items.all().delete()

    return Response(
        {'message': 'Payment verified and order created', 'order_id': order.id},
        status=status.HTTP_201_CREATED,
    )

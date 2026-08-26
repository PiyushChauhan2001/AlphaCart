import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "../utils/auth";
import { useCart } from "../context/CartContext";

function CheckoutPage() {
  const [form, setForm] = useState({
    name: "",
    address: "",
    phone: "",
    payment_method: "COD",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const nav = useNavigate();
  const { clearCart } = useCart();
  const BASEURL = import.meta.env.VITE_DJANGO_BASE_URL;

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const loadRazorpay = () =>
    new Promise((resolve, reject) => {
      if (window.Razorpay) {
        resolve(true);
        return;
      }

      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => reject(new Error("Razorpay could not be loaded"));
      document.body.appendChild(script);
    });

  const createOnlinePayment = async () => {
    const paymentResponse = await authFetch(`${BASEURL}/api/payment/`, {
      method: "POST",
    });
    const paymentData = await paymentResponse.json();

    if (!paymentResponse.ok) {
      throw new Error(paymentData.error || "Unable to start payment");
    }

    await loadRazorpay();

    return new Promise((resolve, reject) => {
      const razorpay = new window.Razorpay({
        key: paymentData.key_id,
        amount: paymentData.amount,
        currency: paymentData.currency,
        name: "Ecommerce Store",
        description: "Order payment",
        order_id: paymentData.payment_order_id,
        prefill: {
          name: form.name,
          contact: form.phone,
        },
        handler: async (response) => {
          try {
            const verifyResponse = await authFetch(`${BASEURL}/api/payment/verify/`, {
              method: "POST",
              body: JSON.stringify(response),
            });
            const verifyData = await verifyResponse.json();

            if (!verifyResponse.ok) {
              reject(new Error(verifyData.error || "Payment verification failed"));
              return;
            }

            resolve(verifyData);
          } catch (error) {
            reject(error);
          }
        },
        modal: {
          ondismiss: () => reject(new Error("Payment was cancelled")),
        },
        theme: { color: "#166534" },
      });

      razorpay.open();
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (form.payment_method === "ONLINE") {
        await createOnlinePayment();
      } else {
        const res = await authFetch(`${BASEURL}/api/orders/create/`, {
          method: "POST",
          body: JSON.stringify(form),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Order failed");
        }
      }

      clearCart();
      alert("Order placed successfully!");
      nav("/");
    } catch (error) {
      console.error("Checkout error:", error);
      alert(error.message || "Checkout failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="pt-20 p-6">
      <div className="max-w-lg mx-auto bg-white p-6 shadow rounded">
        <h1 className="text-2xl font-bold mb-4">Checkout</h1>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Your Name"
            required
            className="w-full p-2 border rounded"
          />

          <input
            name="address"
            value={form.address}
            onChange={handleChange}
            placeholder="Address"
            required
            className="w-full p-2 border rounded"
          />

          <input
            name="phone"
            value={form.phone}
            onChange={handleChange}
            placeholder="Phone Number"
            required
            className="w-full p-2 border rounded"
          />

          <select
            name="payment_method"
            value={form.payment_method}
            onChange={handleChange}
            className="w-full p-2 border rounded"
          >
            <option value="COD">Cash on Delivery</option>
            <option value="ONLINE">Online Payment</option>
          </select>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-green-600 text-white py-2 rounded disabled:opacity-60"
          >
            {isSubmitting
              ? "Processing..."
              : form.payment_method === "ONLINE"
                ? "Pay securely"
                : "Place Order"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CheckoutPage;
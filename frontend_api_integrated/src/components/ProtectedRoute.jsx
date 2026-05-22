import { Navigate } from "react-router-dom";
import useAuthStore from "../store/useAuthStore";

export default function ProtectedRoute({ children, ownerOnly = false }) {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" />;
  if (ownerOnly && user.role !== "owner") return <Navigate to="/home" />;
  return children;
}
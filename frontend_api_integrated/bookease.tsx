import { useState, useEffect, createContext, useContext } from "react";
import { Calendar, Clock, Users, Briefcase, LogOut, Home, ChevronRight, Plus, Edit2, Trash2, CheckCircle, XCircle, AlertCircle, Search, Star, Phone, Mail, ArrowRight, X, Check, Building2, Scissors, Loader } from "lucide-react";
import { appointmentsApi, servicesApi, businessesApi } from "./src/services/api.js";

// ── STORE ────────────────────────────────────────────────────────────
const AuthCtx = createContext(null);
const useAuth = () => useContext(AuthCtx);

// ── MOCK DATA ────────────────────────────────────────────────────────
const BUSINESSES = [
  { id: 1, owner_id: 2, name: "Elite Cuts Barbershop", description: "Premium grooming for the modern gentleman. Expert barbers with 10+ years experience." },
  { id: 2, owner_id: 3, name: "Serenity Spa & Wellness", description: "Holistic wellness treatments. Relax, rejuvenate, and restore your body and mind." },
  { id: 3, owner_id: 4, name: "FitLife Personal Training", description: "Certified trainers helping you reach your fitness goals with personalized plans." },
];
const SERVICES = {
  1: [
    { id: 1, name: "Classic Haircut", description: "Precision cut with hot towel finish", duration_mins: 45, price: 35, requires_advance_deposit: false, is_active: true },
    { id: 2, name: "Beard Trim & Shape", description: "Full beard grooming and styling", duration_mins: 30, price: 25, requires_advance_deposit: false, is_active: true },
    { id: 3, name: "VIP Package", description: "Cut + Beard + Facial treatment", duration_mins: 90, price: 80, requires_advance_deposit: true, is_active: true },
  ],
  2: [
    { id: 4, name: "Swedish Massage", description: "Full body relaxation massage", duration_mins: 60, price: 95, requires_advance_deposit: true, is_active: true },
    { id: 5, name: "Facial Treatment", description: "Deep cleansing and hydration", duration_mins: 45, price: 75, requires_advance_deposit: false, is_active: true },
  ],
  3: [
    { id: 6, name: "Personal Training Session", description: "1-on-1 personalized workout", duration_mins: 60, price: 65, requires_advance_deposit: false, is_active: true },
  ],
};
const HOURS = [
  { id: 1, days_of_week: ["Mon","Tue","Wed","Thu","Fri"], open_time: "09:00", close_time: "18:00", is_open: true },
  { id: 2, days_of_week: ["Sat"], open_time: "10:00", close_time: "16:00", is_open: true },
  { id: 3, days_of_week: ["Sun"], open_time: "00:00", close_time: "00:00", is_open: false },
];
const SAMPLE_APPTS = [
  { id: 1, service_id: 1, service_name: "Classic Haircut", business_name: "Elite Cuts", date: "2026-05-20", time: "10:00", status: "confirmed", payment_status: null },
  { id: 2, service_id: 4, service_name: "Swedish Massage", business_name: "Serenity Spa", date: "2026-05-22", time: "14:00", status: "pending", payment_status: "paid" },
  { id: 3, service_id: 6, service_name: "Personal Training", business_name: "FitLife", date: "2026-05-18", time: "07:00", status: "completed", payment_status: null },
];
const OWNER_APPTS = [
  { id: 10, customer: "Ali Hassan", service: "Classic Haircut", date: "2026-05-20", time: "10:00", status: "confirmed" },
  { id: 11, customer: "Sara Khan", service: "VIP Package", date: "2026-05-20", time: "12:00", status: "pending" },
  { id: 12, customer: "Walk-in Customer", service: "Beard Trim", date: "2026-05-19", time: "09:00", status: "completed" },
  { id: 13, customer: "Ahmed Raza", service: "Classic Haircut", date: "2026-05-19", time: "11:00", status: "no-show" },
];
const CUSTOMERS = [
  { id: 1, name: "Ali Hassan", email: "ali@email.com", phone: "+92 300 1234567" },
  { id: 2, name: "Sara Khan", email: "sara@email.com", phone: "+92 333 9876543" },
  { id: 3, name: "Ahmed Raza", email: "ahmed@email.com", phone: "+92 321 5554444" },
];

// ── UTILS ────────────────────────────────────────────────────────────
const sleep = ms => new Promise(r => setTimeout(r, ms));

function StatusBadge({ status }) {
  const map = {
    pending: "bg-amber-100 text-amber-700",
    confirmed: "bg-emerald-100 text-emerald-700",
    completed: "bg-blue-100 text-blue-700",
    "no-show": "bg-red-100 text-red-700",
    paid: "bg-emerald-100 text-emerald-700",
    unpaid: "bg-gray-100 text-gray-600",
    open: "bg-emerald-100 text-emerald-700",
    closed: "bg-red-100 text-red-700",
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${map[status] || "bg-gray-100 text-gray-600"}`}>{status}</span>;
}

function Toast({ msg, type, onClose }) {
  useEffect(() => { const t = setTimeout(onClose, 3000); return () => clearTimeout(t); }, []);
  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium ${type === "error" ? "bg-red-500" : "bg-emerald-500"}`}>
      {type === "error" ? <XCircle size={16} /> : <CheckCircle size={16} />}
      {msg}
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100"><X size={14} /></button>
    </div>
  );
}

function Spinner() {
  return <div className="flex justify-center py-12"><Loader className="animate-spin text-emerald-500" size={32} /></div>;
}

function EmptyState({ icon: Icon, message }) {
  return (
    <div className="flex flex-col items-center py-16 text-gray-400">
      <Icon size={48} className="mb-3 opacity-30" />
      <p className="text-sm">{message}</p>
    </div>
  );
}

function ConfirmDialog({ msg, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
        <AlertCircle className="text-red-500 mb-3" size={32} />
        <p className="text-gray-700 mb-5">{msg}</p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="flex-1 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm hover:bg-gray-50">Cancel</button>
          <button onClick={onConfirm} className="flex-1 py-2 rounded-lg bg-red-500 text-white text-sm hover:bg-red-600">Delete</button>
        </div>
      </div>
    </div>
  );
}

// ── AUTH PAGES ───────────────────────────────────────────────────────
function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <div className="w-9 h-9 rounded-lg bg-emerald-500 flex items-center justify-center">
              <Calendar size={20} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-white" style={{fontFamily:"system-ui"}}>BookEase</span>
          </div>
          <h1 className="text-xl font-semibold text-white mt-3">{title}</h1>
          {subtitle && <p className="text-slate-400 text-sm mt-1">{subtitle}</p>}
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-2xl">{children}</div>
      </div>
    </div>
  );
}

function Input({ label, type="text", placeholder, value, onChange, error }) {
  return (
    <div className="mb-4">
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <input type={type} placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)}
        className={`w-full px-4 py-2.5 rounded-xl border text-sm outline-none transition ${error ? "border-red-400 bg-red-50" : "border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100"}`} />
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}

function Btn({ children, onClick, variant="primary", size="md", full, loading, className="" }) {
  const base = "inline-flex items-center justify-center gap-2 font-medium rounded-xl transition cursor-pointer";
  const sizes = { sm: "px-3 py-1.5 text-xs", md: "px-4 py-2.5 text-sm", lg: "px-6 py-3 text-base" };
  const variants = {
    primary: "bg-emerald-500 hover:bg-emerald-600 text-white",
    secondary: "border border-gray-200 hover:bg-gray-50 text-gray-700",
    danger: "bg-red-500 hover:bg-red-600 text-white",
    ghost: "text-emerald-600 hover:bg-emerald-50",
    navy: "bg-slate-900 hover:bg-slate-800 text-white",
  };
  return (
    <button onClick={onClick} disabled={loading}
      className={`${base} ${sizes[size]} ${variants[variant]} ${full ? "w-full" : ""} ${loading ? "opacity-70" : ""} ${className}`}>
      {loading && <Loader size={14} className="animate-spin" />}
      {children}
    </button>
  );
}

function LoginPage({ setPage }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [role, setRole] = useState("user");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const submit = async () => {
    if (!email || !pass) { setErr("Please fill all fields"); return; }
    setLoading(true); await sleep(800);
    login({ id: role === "owner" ? 2 : 1, name: role === "owner" ? "Owner User" : "Ali Hassan", email, role });
    setLoading(false);
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your BookEase account">
      <div className="flex rounded-xl border border-gray-200 mb-5 overflow-hidden">
        {["user","owner"].map(r => (
          <button key={r} onClick={() => setRole(r)}
            className={`flex-1 py-2 text-sm font-medium transition ${role === r ? "bg-emerald-500 text-white" : "text-gray-500 hover:bg-gray-50"}`}>
            {r === "user" ? "Customer" : "Business Owner"}
          </button>
        ))}
      </div>
      {err && <p className="text-red-500 text-xs mb-3">{err}</p>}
      <Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={setEmail} />
      <Input label="Password" type="password" placeholder="••••••••" value={pass} onChange={setPass} />
      <div className="text-right mb-4">
        <button onClick={() => setPage("forgot")} className="text-xs text-emerald-600 hover:underline">Forgot password?</button>
      </div>
      <Btn full loading={loading} onClick={submit}>Sign In</Btn>
      <p className="text-center text-sm text-gray-500 mt-4">
        No account? <button onClick={() => setPage("register")} className="text-emerald-600 font-medium hover:underline">Register</button>
      </p>
    </AuthLayout>
  );
}

function RegisterPage({ setPage }) {
  const [form, setForm] = useState({ name:"", email:"", password:"", confirm:"" });
  const [loading, setLoading] = useState(false);
  const f = k => v => setForm(p => ({...p, [k]: v}));
  const submit = async () => { setLoading(true); await sleep(800); setLoading(false); setPage("login"); };
  return (
    <AuthLayout title="Create account" subtitle="Join BookEase today">
      <Input label="Full Name" placeholder="Ali Hassan" value={form.name} onChange={f("name")} />
      <Input label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={f("email")} />
      <Input label="Password" type="password" placeholder="••••••••" value={form.password} onChange={f("password")} />
      <Input label="Confirm Password" type="password" placeholder="••••••••" value={form.confirm} onChange={f("confirm")} />
      <Btn full loading={loading} onClick={submit}>Create Account</Btn>
      <p className="text-center text-sm text-gray-500 mt-4">
        Have account? <button onClick={() => setPage("login")} className="text-emerald-600 font-medium hover:underline">Sign In</button>
      </p>
    </AuthLayout>
  );
}

function ForgotPage({ setPage }) {
  const [email, setEmail] = useState(""); const [sent, setSent] = useState(false); const [loading, setLoading] = useState(false);
  const submit = async () => { setLoading(true); await sleep(700); setLoading(false); setSent(true); };
  return (
    <AuthLayout title="Reset Password" subtitle="We'll send an OTP to your email">
      {sent ? <div className="text-center py-4"><CheckCircle className="text-emerald-500 mx-auto mb-3" size={40} /><p className="text-gray-700 font-medium">OTP sent to your email</p><button onClick={() => setPage("reset")} className="mt-4 text-emerald-600 text-sm hover:underline">Enter OTP →</button></div>
        : <><Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={setEmail} /><Btn full loading={loading} onClick={submit}>Send OTP</Btn></>}
      <p className="text-center text-sm text-gray-500 mt-4"><button onClick={() => setPage("login")} className="text-emerald-600 hover:underline">Back to login</button></p>
    </AuthLayout>
  );
}

// ── NAV ──────────────────────────────────────────────────────────────
function Navbar({ page, setPage }) {
  const { user, logout } = useAuth();
  const [mob, setMob] = useState(false);
  const links = user?.role === "owner"
    ? [["dashboard","Dashboard"],["owner-appts","My Appointments"]]
    : [["home","Home"],["businesses","Businesses"],["appts","My Appointments"]];
  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => setPage(user?.role === "owner" ? "dashboard" : "home")}>
          <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center"><Calendar size={14} className="text-white" /></div>
          <span className="font-bold text-slate-900 text-lg">BookEase</span>
        </div>
        <div className="hidden md:flex items-center gap-1">
          {links.map(([p,l]) => (
            <button key={p} onClick={() => setPage(p)} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${page === p ? "bg-emerald-50 text-emerald-600" : "text-gray-600 hover:bg-gray-50"}`}>{l}</button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden md:block text-sm text-gray-500">{user?.name}</span>
          <Btn size="sm" variant="secondary" onClick={logout}><LogOut size={13} />Logout</Btn>
        </div>
      </div>
    </nav>
  );
}

// ── HOME PAGE ────────────────────────────────────────────────────────
function HomePage({ setPage }) {
  return (
    <div>
      <div className="bg-gradient-to-br from-slate-900 to-slate-700 text-white py-20 px-4 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{fontFamily:"system-ui"}}>Book appointments<br /><span className="text-emerald-400">effortlessly</span></h1>
        <p className="text-slate-300 text-lg mb-8 max-w-xl mx-auto">Discover local businesses and book services in seconds. No waiting, no calls.</p>
        <Btn size="lg" onClick={() => setPage("businesses")}>Browse Businesses <ArrowRight size={16} /></Btn>
      </div>
      <div className="max-w-4xl mx-auto py-16 px-4">
        <h2 className="text-2xl font-bold text-center text-slate-900 mb-10">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[["Find a Business","Search and discover top-rated local businesses",Building2,"1"],
            ["Book a Service","Choose your service, date, and preferred time",Calendar,"2"],
            ["Get Confirmed","Receive instant confirmation and reminders",CheckCircle,"3"]].map(([t,d,Icon,n]) => (
            <div key={t} className="text-center p-6 rounded-2xl border border-gray-100 hover:shadow-md transition">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-4">
                <Icon size={22} className="text-emerald-500" />
              </div>
              <div className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center mx-auto mb-3">{n}</div>
              <h3 className="font-semibold text-slate-900 mb-1">{t}</h3>
              <p className="text-gray-500 text-sm">{d}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── BUSINESSES PAGE ──────────────────────────────────────────────────
function BusinessesPage({ setPage, setBizId, addToast }) {
  const [businesses, setBusinesses] = useState([]);
  const [q, setQ] = useState(""); const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBusinesses = async () => {
      try {
        const { data } = await businessesApi.list();
        setBusinesses(data || []);
      } catch (err) {
        const errMsg = err.response?.data?.detail || err.response?.data?.message || "Failed to fetch businesses";
        setError(errMsg);
        if (addToast) addToast(errMsg, "error");
      } finally {
        setLoading(false);
      }
    };
    fetchBusinesses();
  }, []);

  const filtered = businesses.filter(b => b.name?.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div><h1 className="text-2xl font-bold text-slate-900">Find a Business</h1><p className="text-gray-500 text-sm mt-1">{businesses.length} businesses available</p></div>
        <div className="relative"><Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" /><input placeholder="Search businesses..." value={q} onChange={e => setQ(e.target.value)} className="pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 w-64" /></div>
      </div>
      {loading ? <Spinner /> : error ? (
        <div className="text-center py-12 text-gray-500"><p>{error}</p></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map(b => (
            <div key={b.id} className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-lg transition group">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mb-3"><Briefcase size={18} className="text-emerald-500" /></div>
              <h3 className="font-semibold text-slate-900 mb-1">{b.name}</h3>
              <p className="text-gray-500 text-sm mb-4 line-clamp-2">{b.description || ""}</p>
              <Btn size="sm" onClick={() => { setBizId(b.id); setPage("biz-detail"); }}>View Services <ChevronRight size={14} /></Btn>
            </div>
          ))}
          {!filtered.length && <div className="col-span-3"><EmptyState icon={Search} message="No businesses found" /></div>}
        </div>
      )}
    </div>
  );
}

// ── BOOKING MODAL ────────────────────────────────────────────────────
function BookingModal({ service, onClose, addToast, onBookSuccess }) {
  const { user } = useAuth();
  const [date, setDate] = useState(""); const [time, setTime] = useState(""); const [type, setType] = useState("own");
  const [walkin, setWalkin] = useState({ name:"", phone:"" }); const [loading, setLoading] = useState(false);
  const submit = async () => {
    if (!date || !time) { addToast("Please select date and time", "error"); return; }
    setLoading(true);
    try {
      const startTime = `${date}T${time}:00`;
      await appointmentsApi.create({
        service_id: service.id,
        start_time: startTime,
      });
      addToast("Appointment booked successfully!", "success");
      if (onBookSuccess) onBookSuccess();
      onClose();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || "Failed to book appointment";
      addToast(errorMsg, "error");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <div><h2 className="font-semibold text-slate-900">Book {service.name}</h2><p className="text-xs text-gray-500 mt-0.5">{service.duration_mins} min · ${service.price}</p></div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={18} /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-xs font-medium text-gray-600 mb-1 block">Date</label><input type="date" value={date} onChange={e => setDate(e.target.value)} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
            <div><label className="text-xs font-medium text-gray-600 mb-1 block">Time</label><input type="time" value={time} onChange={e => setTime(e.target.value)} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Customer Type</label>
            <div className="flex rounded-xl border border-gray-200 overflow-hidden">
              {[["own","My Account"],["walkin","Walk-in / Call"]].map(([v,l]) => (
                <button key={v} onClick={() => setType(v)} className={`flex-1 py-2 text-xs font-medium transition ${type===v?"bg-emerald-500 text-white":"text-gray-500 hover:bg-gray-50"}`}>{l}</button>
              ))}
            </div>
          </div>
          {type === "walkin" && (
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs font-medium text-gray-600 mb-1 block">Name</label><input placeholder="Customer name" value={walkin.name} onChange={e => setWalkin(p=>({...p,name:e.target.value}))} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
              <div><label className="text-xs font-medium text-gray-600 mb-1 block">Phone</label><input placeholder="+1 234 567" value={walkin.phone} onChange={e => setWalkin(p=>({...p,phone:e.target.value}))} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
            </div>
          )}
          {service.requires_advance_deposit && <div className="bg-amber-50 rounded-xl px-4 py-2.5 text-xs text-amber-700 flex items-center gap-2"><AlertCircle size={14} />Deposit required — you'll be redirected to payment</div>}
        </div>
        <div className="flex gap-3 p-5 border-t border-gray-100">
          <Btn variant="secondary" full onClick={onClose}>Cancel</Btn>
          <Btn full loading={loading} onClick={submit}>Confirm Booking</Btn>
        </div>
      </div>
    </div>
  );
}

// ── BIZ DETAIL ───────────────────────────────────────────────────────
function BizDetailPage({ bizId, addToast, refreshTrigger }) {
  const [biz, setBiz] = useState(null);
  const [services, setServices] = useState([]);
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [bizRes, servicesRes] = await Promise.all([
          businessesApi.get(bizId),
          servicesApi.listByBusiness(bizId)
        ]);
        setBiz(bizRes.data);
        setServices(servicesRes.data || []);
      } catch (err) {
        const errMsg = err.response?.data?.detail || err.response?.data?.message || "Failed to load business";
        setError(errMsg);
        if (addToast) addToast(errMsg, "error");
      } finally {
        setLoading(false);
      }
    };
    if (bizId) fetchData();
  }, [bizId]);

  if (loading) return <Spinner />;
  if (error || !biz) return <div className="max-w-5xl mx-auto px-4 py-8 text-center text-gray-500">{error || "Business not found"}</div>;

  const allDays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <h1 className="text-2xl font-bold text-slate-900 mb-1">{biz.name}</h1>
        <p className="text-gray-500">{biz.description || ""}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <h2 className="font-semibold text-slate-900 mb-4">Services</h2>
          {services.length === 0 ? <EmptyState icon={Briefcase} message="No services available" /> : (
            <div className="space-y-3">
              {services.map(s => (
                <div key={s.id} className="bg-white rounded-2xl border border-gray-100 p-4 flex items-start justify-between hover:shadow-md transition">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-slate-900">{s.name}</h3>
                      {s.requires_advance_deposit && <span className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded-full">Deposit</span>}
                    </div>
                    <p className="text-gray-500 text-xs mb-2">{s.description || ""}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-400"><Clock size={11}/>{s.duration} min <span className="font-semibold text-slate-900 text-sm">${s.price}</span></div>
                  </div>
                  <Btn size="sm" onClick={() => setBooking(s)}>Book Now</Btn>
                </div>
              ))}
            </div>
          )}
        </div>
        <div>
          <h2 className="font-semibold text-slate-900 mb-4">Working Hours</h2>
          <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            {allDays.map(day => {
              const h = HOURS.find(h => h.days_of_week.includes(day));
              return (
                <div key={day} className="flex items-center justify-between px-4 py-2.5 border-b border-gray-50 last:border-0">
                  <span className="text-sm font-medium text-slate-700">{day}</span>
                  {h?.is_open ? <span className="text-xs text-emerald-600">{h.open_time}–{h.close_time}</span> : <StatusBadge status="closed" />}
                </div>
              );
            })}
          </div>
        </div>
      </div>
      {booking && <BookingModal service={booking} onClose={() => setBooking(null)} addToast={addToast} onBookSuccess={refreshTrigger} />}
    </div>
  );
}

// ── MY APPOINTMENTS ──────────────────────────────────────────────────
function ApptsPage({ setPage, setApptId, refreshTrigger, addToast }) {
  const [appts, setAppts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAppointments = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log("Fetching appointments...");
      const { data } = await appointmentsApi.mine();
      console.log("Appointments response:", data);
      setAppts(data || []);
    } catch (err) {
      console.error("Fetch appointments error:", err);
      const errMsg = err.response?.data?.detail || err.response?.data?.message || err.message || "Failed to fetch appointments";
      setError(errMsg);
      if (addToast) addToast(errMsg, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAppointments(); }, [refreshTrigger]);

  const formatDateTime = (dateStr) => {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toISOString().split('T')[0] + " " + d.toTimeString().split(' ')[0].substring(0, 5);
  };

  const getServiceName = (a) => a.service?.name || a.service?.description || "Service";
  const getBusinessName = (a) => a.business?.name || "Business";

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">My Appointments</h1>
      {loading ? <Spinner /> : error ? (
        <div className="text-center py-12 text-gray-500">
          <p>{error}</p>
          <Btn className="mt-4" onClick={fetchAppointments}>Retry</Btn>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          {appts.length === 0 ? <EmptyState icon={Calendar} message="No appointments yet" /> : (
            <div className="divide-y divide-gray-50">
              {appts.map(a => (
                <div key={a.id} onClick={() => { setApptId(a.id); setPage("appt-detail"); }} className="flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer transition">
                  <div>
                    <p className="font-medium text-slate-900 text-sm">{getServiceName(a)}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{getBusinessName(a)} · {formatDateTime(a.start_time)}</p>
                  </div>
                  <div className="flex items-center gap-2"><StatusBadge status={a.status} /><ChevronRight size={14} className="text-gray-300" /></div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ApptDetailPage({ apptId, addToast }) {
  const [appt, setAppt] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppt = async () => {
      try {
        const { data } = await appointmentsApi.get(apptId);
        setAppt(data);
      } catch (err) {
        addToast(err.response?.data?.detail || err.response?.data?.message || "Failed to load appointment", "error");
      } finally {
        setLoading(false);
      }
    };
    if (apptId) fetchAppt();
  }, [apptId]);

  if (loading) return <Spinner />;
  if (!appt) return <div className="text-center py-12 text-gray-500">Appointment not found</div>;

  const formatDateTime = (dateStr) => {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return d.toISOString().split('T')[0] + " " + d.toTimeString().split(' ')[0].substring(0, 5);
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Appointment Details</h1>
      <div className="bg-white rounded-2xl border border-gray-100 p-6 space-y-4">
        {[["Service", appt.service?.name],["Business", appt.business?.name],["Date & Time", formatDateTime(appt.start_time)]].map(([l,v]) => (
          <div key={l} className="flex justify-between text-sm"><span className="text-gray-500">{l}</span><span className="font-medium text-slate-900">{v || "-"}</span></div>
        ))}
        <div className="flex justify-between text-sm"><span className="text-gray-500">Status</span><StatusBadge status={appt.status} /></div>
        {appt.status === "pending" && (
          <Btn full onClick={async () => {
            try {
              await appointmentsApi.confirm(apptId);
              setAppt(p => ({ ...p, status: "confirmed" }));
              addToast("Appointment confirmed!", "success");
            } catch (err) {
              addToast(err.response?.data?.detail || err.response?.data?.message || "Failed to confirm", "error");
            }
          }}>Confirm Appointment</Btn>
        )}
      </div>
    </div>
  );
}

// ── OWNER DASHBOARD ──────────────────────────────────────────────────
const DASH_TABS = [["overview","Overview"],["services","Services"],["hours","Working Hours"],["owner-appts-mgr","Appointments"],["customers","Customers"]];

function DashboardShell({ active, setPage, children }) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex flex-col md:flex-row gap-6">
        <aside className="md:w-48 shrink-0">
          <nav className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            {DASH_TABS.map(([p,l]) => (
              <button key={p} onClick={() => setPage(p)} className={`w-full text-left px-4 py-3 text-sm font-medium border-b border-gray-50 last:border-0 transition ${active===p?"bg-emerald-50 text-emerald-600":"text-gray-600 hover:bg-gray-50"}`}>{l}</button>
            ))}
          </nav>
        </aside>
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </div>
  );
}

function DashboardOverview({ setPage }) {
  const today = OWNER_APPTS.filter(a => a.date === "2026-05-20");
  const cards = [["Today's Appointments", today.length, Calendar, "emerald"],["Pending", OWNER_APPTS.filter(a=>a.status==="pending").length, AlertCircle, "amber"],["Completed", OWNER_APPTS.filter(a=>a.status==="completed").length, CheckCircle, "blue"]];
  return (
    <DashboardShell active="overview" setPage={setPage}>
      <h1 className="text-xl font-bold text-slate-900 mb-5">Dashboard Overview</h1>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {cards.map(([l,v,Icon,c]) => (
          <div key={l} className="bg-white rounded-2xl border border-gray-100 p-5">
            <div className={`w-9 h-9 rounded-xl bg-${c}-50 flex items-center justify-center mb-3`}><Icon size={18} className={`text-${c}-500`} /></div>
            <p className="text-2xl font-bold text-slate-900">{v}</p>
            <p className="text-xs text-gray-500 mt-0.5">{l}</p>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <div className="flex items-center justify-between mb-4"><h2 className="font-semibold text-slate-900">Business Info</h2><Btn size="sm" variant="secondary"><Edit2 size={12} />Edit</Btn></div>
        <p className="font-medium text-slate-900">Elite Cuts Barbershop</p>
        <p className="text-gray-500 text-sm mt-1">Premium grooming for the modern gentleman.</p>
      </div>
    </DashboardShell>
  );
}

function ServicesManager({ setPage }) {
  const services = SERVICES[1];
  const [showAdd, setShowAdd] = useState(false);
  const [confirm, setConfirm] = useState(null);
  const [form, setForm] = useState({ name:"", description:"", duration_mins:"", price:"", requires_advance_deposit:false, is_active:true });
  const f = k => v => setForm(p=>({...p,[k]:v}));
  return (
    <DashboardShell active="services" setPage={setPage}>
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-slate-900">Services</h1>
        <Btn size="sm" onClick={() => setShowAdd(true)}><Plus size={14} />Add Service</Btn>
      </div>
      <div className="space-y-3">
        {services.map(s => (
          <div key={s.id} className="bg-white rounded-2xl border border-gray-100 p-4 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2"><span className="font-medium text-slate-900 text-sm">{s.name}</span>{s.requires_advance_deposit && <span className="bg-amber-100 text-amber-700 text-xs px-1.5 py-0.5 rounded-full">Deposit</span>}{s.is_active?<StatusBadge status="open"/>:<StatusBadge status="closed"/>}</div>
              <p className="text-xs text-gray-400 mt-0.5">{s.duration_mins} min · ${s.price}</p>
            </div>
            <div className="flex gap-2">
              <Btn size="sm" variant="secondary"><Edit2 size={12} /></Btn>
              <Btn size="sm" variant="secondary" onClick={() => setConfirm(s.id)}><Trash2 size={12} className="text-red-400" /></Btn>
            </div>
          </div>
        ))}
      </div>
      {showAdd && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl p-6">
            <div className="flex items-center justify-between mb-4"><h2 className="font-semibold text-slate-900">Add Service</h2><button onClick={() => setShowAdd(false)}><X size={18} className="text-gray-400" /></button></div>
            <Input label="Name" placeholder="Haircut" value={form.name} onChange={f("name")} />
            <Input label="Description" placeholder="Service description" value={form.description} onChange={f("description")} />
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div><label className="text-xs font-medium text-gray-600 mb-1 block">Duration (mins)</label><input type="number" placeholder="30" value={form.duration_mins} onChange={e=>f("duration_mins")(e.target.value)} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
              <div><label className="text-xs font-medium text-gray-600 mb-1 block">Price ($)</label><input type="number" placeholder="50" value={form.price} onChange={e=>f("price")(e.target.value)} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-emerald-400" /></div>
            </div>
            <div className="flex gap-4 mb-5">
              {[["requires_advance_deposit","Deposit Required"],["is_active","Active"]].map(([k,l]) => (
                <label key={k} className="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                  <div onClick={() => f(k)(!form[k])} className={`w-9 h-5 rounded-full transition ${form[k]?"bg-emerald-500":"bg-gray-200"} relative`}><div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${form[k]?"left-4":"left-0.5"}`} /></div>
                  {l}
                </label>
              ))}
            </div>
            <div className="flex gap-3"><Btn variant="secondary" full onClick={() => setShowAdd(false)}>Cancel</Btn><Btn full onClick={() => setShowAdd(false)}>Save Service</Btn></div>
          </div>
        </div>
      )}
      {confirm && <ConfirmDialog msg="Delete this service? This cannot be undone." onConfirm={() => setConfirm(null)} onCancel={() => setConfirm(null)} />}
    </DashboardShell>
  );
}

function BusinessHoursManager({ setPage, addToast }) {
  const { user } = useAuth();
  const allDays = [
    ["Monday","Mon"],["Tuesday","Tue"],["Wednesday","Wed"],["Thursday","Thu"],
    ["Friday","Fri"],["Saturday","Sat"],["Sunday","Sun"]
  ];
  const emptyRows = () => allDays.map(([day]) => ({ id:null, day_of_week:day, is_open:false, open_time:"09:00", close_time:"17:00" }));
  const [businessId, setBusinessId] = useState(null);
  const [businessName, setBusinessName] = useState("");
  const [hours, setHours] = useState(emptyRows);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const cleanTime = v => (v || "").slice(0, 5);
  const rowPayload = h => ({
    day_of_week: h.day_of_week,
    is_open: !!h.is_open,
    open_time: cleanTime(h.open_time),
    close_time: cleanTime(h.close_time),
  });

  useEffect(() => {
    const loadHours = async () => {
      setLoading(true);
      try {
        const { data: businesses } = await businessesApi.list();
        const ownerBiz = (businesses || []).find(b => String(b.owner_id) === String(user?.id)) || businesses?.[0];
        if (!ownerBiz) { setBusinessId(null); return; }
        setBusinessId(ownerBiz.id);
        setBusinessName(ownerBiz.name || "Selected business");
        const { data } = await businessesApi.hours(ownerBiz.id);
        const apiRows = data || [];
        setHours(emptyRows().map(row => {
          const saved = apiRows.find(h => h.day_of_week === row.day_of_week || h.day === row.day_of_week);
          return saved ? { ...row, id:saved.id, is_open:!!saved.is_open, open_time:cleanTime(saved.open_time) || row.open_time, close_time:cleanTime(saved.close_time) || row.close_time } : row;
        }));
      } catch (err) {
        addToast?.(err.response?.data?.detail || "Failed to load business hours", "error");
      } finally {
        setLoading(false);
      }
    };
    loadHours();
  }, [user?.id]);

  const updateRow = (day, patch) => setHours(rows => rows.map(h => h.day_of_week === day ? { ...h, ...patch } : h));
  const saveHours = async () => {
    if (!businessId) { addToast?.("No business found for this owner", "error"); return; }
    setSaving(true);
    try {
      if (hours.every(h => h.id)) {
        await Promise.all(hours.map(h => businessesApi.updateHour(businessId, h.id, rowPayload(h))));
      } else {
        const { data } = await businessesApi.saveHours(businessId, hours.map(rowPayload));
        setHours(emptyRows().map(row => {
          const saved = (data || []).find(h => h.day_of_week === row.day_of_week);
          return saved ? { ...row, id:saved.id, is_open:!!saved.is_open, open_time:cleanTime(saved.open_time) || row.open_time, close_time:cleanTime(saved.close_time) || row.close_time } : row;
        }));
      }
      addToast?.("Business hours saved", "success");
    } catch (err) {
      addToast?.(err.response?.data?.detail || "Failed to save business hours", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardShell active="hours" setPage={setPage}>
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Working Hours</h1>
          {businessName && <p className="text-xs text-gray-400 mt-0.5">{businessName}</p>}
        </div>
        <Btn size="sm" loading={saving} onClick={saveHours}><Check size={14} />Save Hours</Btn>
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        {loading ? <Spinner /> : !businessId ? <EmptyState icon={Building2} message="No business found" /> : hours.map(h => {
          const shortDay = allDays.find(([day]) => day === h.day_of_week)?.[1] || h.day_of_week;
          return (
            <div key={h.day_of_week} className="grid grid-cols-1 md:grid-cols-[90px_120px_1fr] gap-3 items-center px-5 py-3.5 border-b border-gray-50 last:border-0">
              <span className="font-medium text-slate-900 text-sm">{shortDay}</span>
              <button onClick={() => updateRow(h.day_of_week, { is_open: !h.is_open })} className={`w-24 px-2 py-1.5 rounded-lg text-xs font-medium ${h.is_open ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                {h.is_open ? "Available" : "Closed"}
              </button>
              <div className="grid grid-cols-2 gap-3">
                <input type="time" disabled={!h.is_open} value={h.open_time} onChange={e => updateRow(h.day_of_week, { open_time:e.target.value })} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none disabled:bg-gray-50 disabled:text-gray-300 focus:border-emerald-400" />
                <input type="time" disabled={!h.is_open} value={h.close_time} onChange={e => updateRow(h.day_of_week, { close_time:e.target.value })} className="w-full px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none disabled:bg-gray-50 disabled:text-gray-300 focus:border-emerald-400" />
              </div>
            </div>
          );
        })}
      </div>
    </DashboardShell>
  );
}

function HoursManager({ setPage }) {
  const allDays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  return (
    <DashboardShell active="hours" setPage={setPage}>
      <div className="flex items-center justify-between mb-5"><h1 className="text-xl font-bold text-slate-900">Working Hours</h1><Btn size="sm"><Plus size={14} />Set Hours</Btn></div>
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        {allDays.map(day => {
          const h = HOURS.find(h => h.days_of_week.includes(day));
          return (
            <div key={day} className="flex items-center justify-between px-5 py-3.5 border-b border-gray-50 last:border-0">
              <span className="font-medium text-slate-900 text-sm w-12">{day}</span>
              {h?.is_open ? <span className="text-sm text-gray-600">{h.open_time} – {h.close_time}</span> : <StatusBadge status="closed" />}
              <div className="flex gap-2"><Btn size="sm" variant="secondary"><Edit2 size={12} /></Btn></div>
            </div>
          );
        })}
      </div>
    </DashboardShell>
  );
}

function OwnerApptsMgr({ setPage }) {
  const [filter, setFilter] = useState("all"); const [appts, setAppts] = useState(OWNER_APPTS);
  const shown = filter === "all" ? appts : appts.filter(a => a.status === filter);
  const act = (id, status) => setAppts(p => p.map(a => a.id === id ? {...a, status} : a));
  return (
    <DashboardShell active="owner-appts-mgr" setPage={setPage}>
      <h1 className="text-xl font-bold text-slate-900 mb-5">Appointments</h1>
      <div className="flex gap-2 mb-4 flex-wrap">
        {["all","pending","confirmed","completed","no-show"].map(f => (
          <button key={f} onClick={() => setFilter(f)} className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${filter===f?"bg-slate-900 text-white":"bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"}`}>{f}</button>
        ))}
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        {shown.length === 0 ? <EmptyState icon={Calendar} message="No appointments" /> : (
          <div className="divide-y divide-gray-50">
            {shown.map(a => (
              <div key={a.id} className="flex items-center justify-between p-4">
                <div>
                  <p className="font-medium text-slate-900 text-sm">{a.customer}</p>
                  <p className="text-xs text-gray-400">{a.service} · {a.date} {a.time}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={a.status} />
                  {a.status === "confirmed" && <Btn size="sm" onClick={() => act(a.id,"completed")}>Complete</Btn>}
                  {(a.status==="pending"||a.status==="confirmed") && <Btn size="sm" variant="secondary" onClick={() => act(a.id,"no-show")}>No-show</Btn>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}

function CustomersManager({ setPage }) {
  const [customers, setCustomers] = useState(CUSTOMERS);
  const [confirm, setConfirm] = useState(null);
  return (
    <DashboardShell active="customers" setPage={setPage}>
      <div className="flex items-center justify-between mb-5"><h1 className="text-xl font-bold text-slate-900">Customers</h1><Btn size="sm"><Plus size={14} />Add Customer</Btn></div>
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        {customers.map(c => (
          <div key={c.id} className="flex items-center justify-between p-4 border-b border-gray-50 last:border-0">
            <div>
              <p className="font-medium text-slate-900 text-sm">{c.name}</p>
              <div className="flex gap-3 text-xs text-gray-400 mt-0.5"><span className="flex items-center gap-1"><Mail size={10}/>{c.email}</span><span className="flex items-center gap-1"><Phone size={10}/>{c.phone}</span></div>
            </div>
            <div className="flex gap-2">
              <Btn size="sm" variant="secondary"><Edit2 size={12} /></Btn>
              <Btn size="sm" variant="secondary" onClick={() => setConfirm(c.id)}><Trash2 size={12} className="text-red-400" /></Btn>
            </div>
          </div>
        ))}
      </div>
      {confirm && <ConfirmDialog msg="Delete this customer?" onConfirm={() => { setCustomers(p=>p.filter(c=>c.id!==confirm)); setConfirm(null); }} onCancel={() => setConfirm(null)} />}
    </DashboardShell>
  );
}

// ── APP ──────────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("login");
  const [bizId, setBizId] = useState(null);
  const [apptId, setApptId] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const addToast = (msg, type="success") => {
    const id = Date.now();
    setToasts(p => [...p, { id, msg, type }]);
  };
  const removeToast = id => setToasts(p => p.filter(t => t.id !== id));

  const auth = {
    user,
    login: u => { 
      localStorage.setItem('access_token', 'mock_token_for_testing');
      setUser(u); 
      setPage(u.role === "owner" ? "dashboard" : "home"); 
    },
    logout: () => { setUser(null); setPage("login"); },
  };

  const renderPage = () => {
    if (!user) {
      if (page === "register") return <RegisterPage setPage={setPage} />;
      if (page === "forgot") return <ForgotPage setPage={setPage} />;
      return <LoginPage setPage={setPage} />;
    }
    switch (page) {
      case "home": return <HomePage setPage={setPage} />;
      case "businesses": return <BusinessesPage setPage={setPage} setBizId={setBizId} />;
      case "biz-detail": return <BizDetailPage bizId={bizId} addToast={addToast} refreshTrigger={() => setRefreshTrigger(p => p + 1)} />;
      case "appts": return <ApptsPage setPage={setPage} setApptId={setApptId} refreshTrigger={refreshTrigger} addToast={addToast} />;
      case "appt-detail": return <ApptDetailPage apptId={apptId} addToast={addToast} />;
      case "owner-appts": return <ApptsPage setPage={setPage} setApptId={setApptId} refreshTrigger={refreshTrigger} addToast={addToast} />;
      case "dashboard": return <DashboardOverview setPage={setPage} />;
      case "services": return <ServicesManager setPage={setPage} />;
      case "hours": return <BusinessHoursManager setPage={setPage} addToast={addToast} />;
      case "owner-appts-mgr": return <OwnerApptsMgr setPage={setPage} />;
      case "customers": return <CustomersManager setPage={setPage} />;
      case "payment/success": return <div className="text-center py-24"><CheckCircle className="text-emerald-500 mx-auto mb-4" size={48}/><h2 className="text-xl font-bold text-slate-900">Payment Successful!</h2><p className="text-gray-500 mt-2">Your appointment is confirmed.</p><Btn className="mt-6" onClick={() => setPage("appts")}>View Appointments</Btn></div>;
      case "payment/cancel": return <div className="text-center py-24"><XCircle className="text-red-400 mx-auto mb-4" size={48}/><h2 className="text-xl font-bold text-slate-900">Payment Cancelled</h2><Btn className="mt-6" onClick={() => setPage("businesses")}>Back to Businesses</Btn></div>;
      default: return <HomePage setPage={setPage} />;
    }
  };

  return (
    <AuthCtx.Provider value={auth}>
      <div className="min-h-screen bg-gray-50 font-sans">
        {user && <Navbar page={page} setPage={setPage} />}
        {renderPage()}
        {toasts.map(t => <Toast key={t.id} msg={t.msg} type={t.type} onClose={() => removeToast(t.id)} />)}
      </div>
    </AuthCtx.Provider>
  );
}

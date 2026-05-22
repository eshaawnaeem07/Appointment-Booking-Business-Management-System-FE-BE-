import { useEffect, useMemo, useState } from 'react';
import { Calendar, Clock, Building2, LogOut, Plus, RefreshCw, Trash2, Check, Eye, Mail, Pencil, Phone, Save, UserRound, X } from 'lucide-react';
import { appointmentsApi, authApi, businessesApi, servicesApi } from './services/api';

type User = { email: string; role: string };
type Business = { id: string; name: string; description?: string; owner_id?: string };
type Service = { id: string; business_id: string; name: string; description?: string; duration: number; price: number; requires_deposit: boolean };
type Appointment = { id: string; business_id: string; service_id: string; start_time: string; end_time: string; status: string };
type BusinessHour = { id?: string; day_of_week: string; is_open: boolean; open_time: string; close_time: string };
type AvailableDay = { date: string; available_slots: string[] };
type BusinessCustomer = { id: string; business_id: string; user_id?: string | null; name: string; phone: string; email?: string | null; created_at: string };

const decodeUser = (token: string, fallbackEmail = ''): User => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return { email: payload.sub || fallbackEmail, role: payload.role || 'user' };
  } catch {
    return { email: fallbackEmail, role: 'user' };
  }
};

const money = (value: number) => new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(Number(value || 0));
const formatDateTime = (value: string) => value ? new Date(value).toLocaleString() : '-';
const formatDate = (value: string) => value ? new Date(value).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : '-';
const formatTime = (value: string) => value ? new Date(value).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) : '-';

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>;
}

function Button({ children, onClick, type = 'button', variant = 'primary', disabled = false, className = '' }: any) {
  const styles = variant === 'secondary'
    ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
    : variant === 'danger'
      ? 'bg-red-600 text-white hover:bg-red-700'
      : 'bg-slate-900 text-white hover:bg-slate-800';
  return <button type={type} disabled={disabled} onClick={onClick} className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium disabled:opacity-50 ${styles} ${className}`}>{children}</button>;
}

function Input(props: any) {
  return <input {...props} className={`w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-500 ${props.className || ''}`} />;
}

function Select(props: any) {
  return <select {...props} className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-500" />;
}

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  });
  const [authMode, setAuthMode] = useState<'login' | 'register' | 'forgot' | 'reset'>('login');
  const [authForm, setAuthForm] = useState({ email: '', password: '', role: 'user' });
  const [forgotForm, setForgotForm] = useState({ email: '' });
  const [resetForm, setResetForm] = useState({ email: '', otp: '', new_password: '', confirm_password: '' });
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState('');
  const [services, setServices] = useState<Service[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [businessAppointments, setBusinessAppointments] = useState<Appointment[]>([]);
  const [customers, setCustomers] = useState<BusinessCustomer[]>([]);
  const defaultHours = (): BusinessHour[] => ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day) => ({
    day_of_week: day,
    is_open: false,
    open_time: '09:00',
    close_time: '17:00',
  }));
  const [businessHours, setBusinessHours] = useState<BusinessHour[]>(defaultHours);
  const [serviceNamesById, setServiceNamesById] = useState<Record<string, string>>({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [businessForm, setBusinessForm] = useState({ name: '', description: '' });
  const [serviceForm, setServiceForm] = useState({ name: '', description: '', duration: '30', price: '0', requires_deposit: false });
  const emptyCustomerForm = { name: '', phone: '', email: '' };
  const [customerForm, setCustomerForm] = useState(emptyCustomerForm);
  const [editingCustomerId, setEditingCustomerId] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<BusinessCustomer | null>(null);
  const [bookingForm, setBookingForm] = useState({ service_id: '', start_time: '' });
  const [availableDays, setAvailableDays] = useState<AvailableDay[]>([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<any>(null);
  const [showAppointmentModal, setShowAppointmentModal] = useState(false);

  const isBusinessUser = user?.role === 'business';
  const selectedBusiness = useMemo(() => businesses.find((b) => b.id === selectedBusinessId), [businesses, selectedBusinessId]);
  const getServiceName = (serviceId: string) => serviceNamesById[serviceId] || services.find((service) => service.id === serviceId)?.name || 'Service unavailable';
  const getBusinessName = (businessId: string) => businesses.find((business) => business.id === businessId)?.name || 'Business unavailable';
  const getAppointmentUserName = (appointment: any) => appointment.walk_in_customer?.name || appointment.user?.email || appointment.user_name || appointment.customer_name || appointment.user_id || '-';

  const showError = (error: any) => setMessage(error?.response?.data?.detail || error?.message || 'Something went wrong');

  const loadBusinesses = async () => {
    const { data } = await businessesApi.list();
    let visibleBusinesses = data || [];

    if (isBusinessUser) {
      const ownershipChecks = await Promise.allSettled(
        visibleBusinesses.map(async (business: Business) => {
          await businessesApi.appointments(business.id);
          return business;
        })
      );

      visibleBusinesses = ownershipChecks
        .filter((result): result is PromiseFulfilledResult<Business> => result.status === 'fulfilled')
        .map((result) => result.value);
    }

    setBusinesses(visibleBusinesses);
    setSelectedBusinessId((current) => visibleBusinesses.some((business: Business) => business.id === current) ? current : visibleBusinesses?.[0]?.id || '');
  };

  const loadServices = async (businessId: string) => {
    if (!businessId) return setServices([]);
    const { data } = await servicesApi.listByBusiness(businessId);
    setServices(data);
    setBookingForm((prev) => ({ ...prev, service_id: data?.[0]?.id || '' }));
  };

  const loadMyAppointments = async () => {
    if (!user) return;
    try {
      const { data } = await appointmentsApi.mine();
      setAppointments(data || []);
    } catch (error) {
      console.error("Failed to load appointments:", error);
      setMessage(error?.response?.data?.detail || error?.message || 'Failed to fetch appointments');
    }
  };

  const loadBusinessAppointments = async (businessId: string) => {
    if (!businessId || !isBusinessUser) return setBusinessAppointments([]);
    const { data } = await businessesApi.appointments(businessId);
    setBusinessAppointments(data);
  };

  const loadCustomers = async (businessId: string) => {
    if (!businessId || !isBusinessUser) {
      setCustomers([]);
      setSelectedCustomer(null);
      return;
    }

    const { data } = await businessesApi.customers(businessId);
    const customerRows = data || [];
    setCustomers(customerRows);
    setSelectedCustomer((current) => current && customerRows.some((customer: BusinessCustomer) => customer.id === current.id) ? current : null);
  };

  const loadBusinessHours = async (businessId: string) => {
    if (!businessId || !isBusinessUser) return setBusinessHours(defaultHours());
    const { data } = await businessesApi.hours(businessId);
    const rows = defaultHours();
    setBusinessHours(rows.map((row) => {
      const saved = (data || []).find((hour: any) => hour.day_of_week === row.day_of_week);
      return saved ? {
        ...row,
        id: saved.id,
        is_open: !!saved.is_open,
        open_time: (saved.open_time || row.open_time).slice(0, 5),
        close_time: (saved.close_time || row.close_time).slice(0, 5),
      } : row;
    }));
  };

  const viewAppointment = async (appointmentId: string) => {
    try {
      setLoading(true);
      const { data } = await appointmentsApi.get(appointmentId);
      setSelectedAppointment(data);
      setShowAppointmentModal(true);
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  const refreshAll = async () => {
    try {
      setLoading(true);
      await loadBusinesses();
      await loadMyAppointments();
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (user) refreshAll(); }, [user]);
  useEffect(() => {
    if (selectedBusinessId) {
      loadServices(selectedBusinessId).catch(showError);
      loadBusinessAppointments(selectedBusinessId).catch(showError);
      loadBusinessHours(selectedBusinessId).catch(showError);
      loadCustomers(selectedBusinessId).catch(showError);
      return;
    }

    setServices([]);
    setBusinessAppointments([]);
    setCustomers([]);
    setSelectedCustomer(null);
    setEditingCustomerId('');
    setCustomerForm(emptyCustomerForm);
    setBusinessHours(defaultHours());
    setAvailableDays([]);
    setBookingForm({ service_id: '', start_time: '' });
  }, [selectedBusinessId, isBusinessUser]);
  useEffect(() => {
    if (!services.length) return;

    setServiceNamesById((current) => ({
      ...current,
      ...Object.fromEntries(services.map((service) => [service.id, service.name])),
    }));
  }, [services]);
  useEffect(() => {
    const serviceIds = [...appointments, ...businessAppointments].map((appointment) => appointment.service_id).filter(Boolean);
    const missingServiceIds = Array.from(new Set(serviceIds)).filter((id) => !serviceNamesById[id]);

    if (!missingServiceIds.length) return;

    let isMounted = true;
    Promise.all(
      missingServiceIds.map(async (serviceId) => {
        try {
          const { data } = await servicesApi.get(serviceId);
          return [serviceId, data?.name || 'Service unavailable'] as const;
        } catch {
          return [serviceId, 'Service unavailable'] as const;
        }
      })
    ).then((entries) => {
      if (!isMounted) return;
      setServiceNamesById((current) => ({
        ...current,
        ...Object.fromEntries(entries),
      }));
    });

    return () => { isMounted = false; };
  }, [appointments, businessAppointments, serviceNamesById]);

  const submitAuth = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      setMessage('');
      if (authMode === 'register') {
        await authApi.register(authForm);
        setAuthMode('login');
        setMessage('Account created. Please login now.');
        return;
      }
      const { data } = await authApi.login({ email: authForm.email, password: authForm.password });
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      const userData = decodeUser(data.access_token, authForm.email);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  const submitForgotPassword = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      setMessage('');
      await authApi.forgotPassword(forgotForm);
      setResetForm((current) => ({ ...current, email: forgotForm.email }));
      setAuthMode('reset');
      setMessage('OTP sent to your email.');
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  const submitResetPassword = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      setMessage('');
      await authApi.resetPassword(resetForm);
      setAuthMode('login');
      setAuthForm((current) => ({ ...current, email: resetForm.email, password: '' }));
      setResetForm({ email: '', otp: '', new_password: '', confirm_password: '' });
      setForgotForm({ email: '' });
      setMessage('Password updated successfully. Please login now.');
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    setBusinesses([]);
    setServices([]);
    setAppointments([]);
    setCustomers([]);
    setSelectedCustomer(null);
    resetCustomerForm();
  };

  const createBusiness = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      const { data } = await businessesApi.create(businessForm);
      setBusinessForm({ name: '', description: '' });
      setSelectedBusinessId(data.id);
      await loadBusinesses();
      setMessage('Business created successfully.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const createService = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      await servicesApi.create(selectedBusinessId, {
        name: serviceForm.name,
        description: serviceForm.description,
        duration: Number(serviceForm.duration),
        price: Number(serviceForm.price),
        requires_deposit: serviceForm.requires_deposit,
      });
      setServiceForm({ name: '', description: '', duration: '30', price: '0', requires_deposit: false });
      await loadServices(selectedBusinessId);
      setMessage('Service created successfully.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const deleteService = async (serviceId: string) => {
    try {
      setLoading(true);
      await servicesApi.remove(serviceId);
      await loadServices(selectedBusinessId);
      setMessage('Service deleted.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const resetCustomerForm = () => {
    setCustomerForm(emptyCustomerForm);
    setEditingCustomerId('');
  };

  const viewCustomer = async (customerId: string) => {
    try {
      setLoading(true);
      const { data } = await businessesApi.getCustomer(selectedBusinessId, customerId);
      setSelectedCustomer(data);
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const startEditCustomer = (customer: BusinessCustomer) => {
    setEditingCustomerId(customer.id);
    setCustomerForm({ name: customer.name, phone: customer.phone, email: customer.email || '' });
  };

  const saveCustomer = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      const payload = {
        name: customerForm.name.trim(),
        phone: customerForm.phone.trim(),
        email: customerForm.email.trim() || null,
      };

      if (editingCustomerId) {
        const { data } = await businessesApi.updateCustomer(selectedBusinessId, editingCustomerId, payload);
        setSelectedCustomer((current) => current?.id === editingCustomerId ? data : current);
        setMessage('Customer updated successfully.');
      } else {
        const { data } = await businessesApi.createCustomer(selectedBusinessId, payload);
        setSelectedCustomer(data);
        setMessage('Customer created successfully.');
      }

      resetCustomerForm();
      await loadCustomers(selectedBusinessId);
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const deleteCustomer = async (customerId: string) => {
    if (!window.confirm('Delete this customer?')) return;
    try {
      setLoading(true);
      await businessesApi.deleteCustomer(selectedBusinessId, customerId);
      setSelectedCustomer((current) => current?.id === customerId ? null : current);
      if (editingCustomerId === customerId) resetCustomerForm();
      await loadCustomers(selectedBusinessId);
      setMessage('Customer deleted.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const updateHourRow = (day: string, patch: Partial<BusinessHour>) => {
    setBusinessHours((rows) => rows.map((row) => row.day_of_week === day ? { ...row, ...patch } : row));
  };

  const saveBusinessHours = async () => {
    try {
      setLoading(true);
      const payload = businessHours.map((hour) => ({
        day_of_week: hour.day_of_week,
        is_open: hour.is_open,
        open_time: hour.open_time,
        close_time: hour.close_time,
      }));

      if (businessHours.every((hour) => hour.id)) {
        await Promise.all(businessHours.map((hour, index) => businessesApi.updateHour(selectedBusinessId, hour.id, payload[index])));
      } else {
        await businessesApi.saveHours(selectedBusinessId, payload);
      }

      await loadBusinessHours(selectedBusinessId);
      setMessage('Business hours saved successfully.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const bookAppointment = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      setLoading(true);
      await appointmentsApi.create({ service_id: bookingForm.service_id, start_time: bookingForm.start_time });
      await loadMyAppointments();
      await loadBusinessAppointments(selectedBusinessId);
      setMessage('Appointment booked successfully.');
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const loadAvailableSlots = async () => {
    if (!bookingForm.service_id) {
      setMessage('Select a service first.');
      return;
    }

    try {
      setSlotsLoading(true);
      setMessage('');
      const selectedDate = bookingForm.start_time ? bookingForm.start_time.slice(0, 10) : undefined;
      const { data } = await servicesApi.availableSlots(bookingForm.service_id, selectedDate);
      const now = new Date();
      const futureDays = (data?.days || [])
        .map((day: AvailableDay) => ({
          ...day,
          available_slots: day.available_slots.filter((slot) => new Date(slot) > now),
        }))
        .filter((day: AvailableDay) => day.available_slots.length > 0);
      setAvailableDays(futureDays);
    } catch (error) {
      showError(error);
    } finally {
      setSlotsLoading(false);
    }
  };

  const selectSlot = (slot: string) => {
    const localValue = slot.slice(0, 16);
    setBookingForm((current) => ({ ...current, start_time: localValue }));
  };

  const updateAppointmentStatus = async (id: string, action: 'confirm' | 'complete' | 'noShow') => {
    try {
      setLoading(true);
      await appointmentsApi[action](id);
      await loadBusinessAppointments(selectedBusinessId);
      await loadMyAppointments();
    } catch (error) { showError(error); } finally { setLoading(false); }
  };

  const confirmAppointment = async (appointmentId: string) => {
    try {
      setLoading(true);
      const { data } = await appointmentsApi.confirm(appointmentId);
      await loadBusinessAppointments(selectedBusinessId);
      await loadMyAppointments();
      setSelectedAppointment(data);
      setMessage('Appointment confirmed.');
      setShowAppointmentModal(false);
    } catch (error) {
      showError(error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
        <Card className="w-full max-w-md">
          <div className="mb-6 text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white"><Calendar /></div>
            <h1 className="text-2xl font-bold text-slate-900">BookEase</h1>
            <p className="text-sm text-slate-500">
              {authMode === 'login' && 'Login with your FastAPI backend account'}
              {authMode === 'register' && 'Create a backend account'}
              {authMode === 'forgot' && 'Request an OTP to reset your password'}
              {authMode === 'reset' && 'Reset password with your email and OTP'}
            </p>
          </div>
          {message && <p className="mb-4 rounded-xl bg-slate-100 p-3 text-sm text-slate-700">{message}</p>}
          {(authMode === 'login' || authMode === 'register') && (
            <>
              <form onSubmit={submitAuth} className="space-y-3">
                <Input type="email" placeholder="Email" value={authForm.email} onChange={(e: any) => setAuthForm({ ...authForm, email: e.target.value })} required />
                <Input type="password" placeholder="Password" value={authForm.password} onChange={(e: any) => setAuthForm({ ...authForm, password: e.target.value })} required />
                {authMode === 'register' && <Select value={authForm.role} onChange={(e: any) => setAuthForm({ ...authForm, role: e.target.value })}><option value="user">Customer</option><option value="business">Business Owner</option></Select>}
                <Button type="submit" disabled={loading}>{loading ? 'Please wait...' : authMode === 'login' ? 'Login' : 'Register'}</Button>
              </form>
              <div className="mt-4 flex flex-col gap-3 text-sm">
                {authMode === 'login' && <button className="text-left font-medium text-slate-700" onClick={() => { setForgotForm({ email: authForm.email }); setAuthMode('forgot'); }}>Forgot password?</button>}
                <button className="text-left font-medium text-slate-700" onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}>
                  {authMode === 'login' ? 'Need an account? Register' : 'Already have account? Login'}
                </button>
              </div>
            </>
          )}
          {authMode === 'forgot' && (
            <>
              <form onSubmit={submitForgotPassword} className="space-y-3">
                <Input type="email" placeholder="Email" value={forgotForm.email} onChange={(e: any) => setForgotForm({ email: e.target.value })} required />
                <Button type="submit" disabled={loading}>{loading ? 'Please wait...' : 'Send OTP'}</Button>
              </form>
              <div className="mt-4 flex flex-col gap-3 text-sm">
                <button className="text-left font-medium text-slate-700" onClick={() => { setResetForm((current) => ({ ...current, email: forgotForm.email })); setAuthMode('reset'); }}>Already have OTP? Reset password</button>
                <button className="text-left font-medium text-slate-700" onClick={() => setAuthMode('login')}>Back to login</button>
              </div>
            </>
          )}
          {authMode === 'reset' && (
            <>
              <form onSubmit={submitResetPassword} className="space-y-3">
                <Input type="email" placeholder="Email" value={resetForm.email} onChange={(e: any) => setResetForm({ ...resetForm, email: e.target.value })} required />
                <Input type="text" placeholder="OTP" value={resetForm.otp} onChange={(e: any) => setResetForm({ ...resetForm, otp: e.target.value })} required />
                <Input type="password" placeholder="New Password" value={resetForm.new_password} onChange={(e: any) => setResetForm({ ...resetForm, new_password: e.target.value })} required />
                <Input type="password" placeholder="Confirm Password" value={resetForm.confirm_password} onChange={(e: any) => setResetForm({ ...resetForm, confirm_password: e.target.value })} required />
                <Button type="submit" disabled={loading}>{loading ? 'Please wait...' : 'Reset Password'}</Button>
              </form>
              <div className="mt-4 flex flex-col gap-3 text-sm">
                <button className="text-left font-medium text-slate-700" onClick={() => setAuthMode('forgot')}>Request a new OTP</button>
                <button className="text-left font-medium text-slate-700" onClick={() => setAuthMode('login')}>Back to login</button>
              </div>
            </>
          )}
        </Card>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-8">
      <div className="mx-auto max-w-6xl space-y-5">
        <header className="flex flex-col gap-3 rounded-2xl bg-slate-900 p-5 text-white md:flex-row md:items-center md:justify-between">
          <div><h1 className="text-2xl font-bold">BookEase API Integrated</h1><p className="text-sm text-slate-300">Logged in as {user.email} · role: {user.role}</p></div>
          <div className="flex gap-2"><Button variant="secondary" onClick={refreshAll}><RefreshCw size={16} /> Refresh</Button><Button variant="danger" onClick={logout}><LogOut size={16} /> Logout</Button></div>
        </header>

        {message && <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-700">{message}</div>}

        <section className="grid gap-5 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <div className="mb-4 flex items-center gap-2"><Building2 size={20} /><h2 className="text-lg font-semibold">Businesses</h2></div>
            <Select value={selectedBusinessId} onChange={(e: any) => setSelectedBusinessId(e.target.value)}>
              <option value="">Select business</option>
              {businesses.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </Select>
            {selectedBusiness && <p className="mt-3 text-sm text-slate-500">{selectedBusiness.description || 'No description'}</p>}
          </Card>

        </section>

        {isBusinessUser && !selectedBusinessId && <Card>
          <h2 className="mb-4 text-lg font-semibold">Create Your Business</h2>
          <form className="space-y-3 md:grid md:grid-cols-[1fr_2fr_auto] md:items-end md:gap-3 md:space-y-0" onSubmit={createBusiness}>
            <label className="block text-sm font-medium text-slate-700">
              Name
              <Input className="mt-1" placeholder="Business name" value={businessForm.name} onChange={(e: any) => setBusinessForm({ ...businessForm, name: e.target.value })} required />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Description
              <Input className="mt-1" placeholder="Business description" value={businessForm.description} onChange={(e: any) => setBusinessForm({ ...businessForm, description: e.target.value })} />
            </label>
            <Button type="submit" disabled={loading} className="w-full md:w-auto"><Plus size={16} />Create Business</Button>
          </form>
        </Card>}

        {selectedBusinessId && <section className="grid gap-5 lg:grid-cols-2">
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Services</h2>
            <div className="space-y-3">
              {services.map((service) => <div key={service.id} className="rounded-xl border border-slate-200 p-3">
                <div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold">{service.name}</h3><p className="text-sm text-slate-500">{service.description}</p><p className="mt-1 text-sm"><Clock className="mr-1 inline" size={14} />{service.duration} min · {money(service.price)} {service.requires_deposit ? '· deposit required' : ''}</p></div>{isBusinessUser && <Button variant="danger" onClick={() => deleteService(service.id)}><Trash2 size={14} /></Button>}</div>
              </div>)}
              {!services.length && <p className="text-sm text-slate-500">No services found for selected business.</p>}
            </div>
          </Card>

          <Card>
            <h2 className="mb-4 text-lg font-semibold">Book Appointment</h2>
            <form className="space-y-3" onSubmit={bookAppointment}>
              <Select value={bookingForm.service_id} onChange={(e: any) => { setBookingForm({ ...bookingForm, service_id: e.target.value }); setAvailableDays([]); }} required>
                <option value="">Select service</option>
                {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </Select>
              <div className="flex gap-2">
                <Input className="booking-date-time-input" type="datetime-local" value={bookingForm.start_time} onChange={(e: any) => setBookingForm({ ...bookingForm, start_time: e.target.value })} required />
                <Button variant="secondary" onClick={loadAvailableSlots} disabled={slotsLoading || !bookingForm.service_id} className="shrink-0 px-3" title="Load available slots">
                  <Calendar size={16} />
                </Button>
              </div>
              {!!availableDays.length && (
                <div className="max-h-56 overflow-y-auto rounded-xl border border-slate-200 p-3">
                  <p className="mb-2 text-sm font-semibold text-slate-700">Available slots</p>
                  <div className="space-y-3">
                    {availableDays.map((day) => (
                      <div key={day.date}>
                        <p className="mb-2 text-xs font-semibold uppercase text-slate-500">{formatDate(day.date)}</p>
                        <div className="flex flex-wrap gap-2">
                          {day.available_slots.map((slot) => (
                            <button
                              key={slot}
                              type="button"
                              onClick={() => selectSlot(slot)}
                              className={`rounded-lg border px-3 py-1.5 text-sm font-medium ${bookingForm.start_time === slot.slice(0, 16) ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}
                            >
                              {formatTime(slot)}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {slotsLoading && <p className="text-sm text-slate-500">Loading available slots...</p>}
              <Button type="submit" disabled={loading || !bookingForm.service_id}>Book</Button>
            </form>
          </Card>
        </section>}

        {isBusinessUser && selectedBusinessId && <Card>
          <h2 className="mb-4 text-lg font-semibold">Add Service for Selected Business</h2>
          <form className="space-y-3 md:space-y-0 md:grid md:gap-3 md:grid-cols-5 md:items-end" onSubmit={createService}>
            <label className="block text-sm font-medium text-slate-700">
              Name
              <Input className="mt-1" placeholder="Name" value={serviceForm.name} onChange={(e: any) => setServiceForm({ ...serviceForm, name: e.target.value })} required />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Description
              <Input className="mt-1" placeholder="Description" value={serviceForm.description} onChange={(e: any) => setServiceForm({ ...serviceForm, description: e.target.value })} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Duration
              <Input className="mt-1" type="number" placeholder="Duration" value={serviceForm.duration} onChange={(e: any) => setServiceForm({ ...serviceForm, duration: e.target.value })} required />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Price
              <Input className="mt-1" type="number" placeholder="Price" value={serviceForm.price} onChange={(e: any) => setServiceForm({ ...serviceForm, price: e.target.value })} required />
            </label>
            <Button type="submit" disabled={loading} className="w-full md:w-auto">Add Service</Button>
          </form>
        </Card>}

        {isBusinessUser && selectedBusinessId && <section className="grid gap-5 lg:grid-cols-[1.5fr_1fr]">
          <Card>
            <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="flex items-center gap-2"><UserRound size={20} /><h2 className="text-lg font-semibold">Business Customers</h2></div>
                <p className="text-sm text-slate-500">{customers.length} saved for {selectedBusiness?.name || 'selected business'}</p>
              </div>
              {/* <Button variant="secondary" onClick={() => loadCustomers(selectedBusinessId)} disabled={loading}><RefreshCw size={16} />Reload</Button> */}
            </div>
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-2 font-semibold">Name</th>
                    <th className="px-3 py-2 font-semibold">Phone</th>
                    <th className="px-3 py-2 font-semibold">Email</th>
                    <th className="px-3 py-2 font-semibold">Created</th>
                    <th className="px-3 py-2 text-right font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {customers.map((customer) => (
                    <tr key={customer.id} className="bg-white align-top">
                      <td className="px-3 py-3 font-medium text-slate-900">{customer.name}</td>
                      <td className="px-3 py-3 text-slate-700">{customer.phone}</td>
                      <td className="px-3 py-3 text-slate-700">{customer.email || '-'}</td>
                      <td className="px-3 py-3 text-slate-700">{formatDate(customer.created_at)}</td>
                      <td className="px-3 py-3">
                        <div className="flex justify-end gap-2">
                          <Button variant="secondary" onClick={() => viewCustomer(customer.id)} className="px-3"><Eye size={14} /></Button>
                          <Button variant="secondary" onClick={() => startEditCustomer(customer)} className="px-3"><Pencil size={14} /></Button>
                          <Button variant="danger" onClick={() => deleteCustomer(customer.id)} className="px-3"><Trash2 size={14} /></Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!customers.length && <p className="bg-white p-3 text-sm text-slate-500">No customers found for selected business.</p>}
            </div>
            {selectedCustomer && (
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-slate-900">{selectedCustomer.name}</h3>
                    <p className="text-xs text-slate-500">Customer ID: {selectedCustomer.id}</p>
                  </div>
                  <Button variant="secondary" onClick={() => setSelectedCustomer(null)} className="px-3"><X size={14} /></Button>
                </div>
                <div className="grid gap-3 text-sm md:grid-cols-3">
                  <div className="flex items-center gap-2 text-slate-700"><Phone size={14} />{selectedCustomer.phone}</div>
                  <div className="flex items-center gap-2 text-slate-700"><Mail size={14} />{selectedCustomer.email || 'No email'}</div>
                  <div className="text-slate-700">Created {formatDateTime(selectedCustomer.created_at)}</div>
                </div>
              </div>
            )}
          </Card>

          <Card>
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold">{editingCustomerId ? 'Edit Customer' : 'Create Customer'}</h2>
              {editingCustomerId && <Button variant="secondary" onClick={resetCustomerForm} className="px-3"><X size={14} /></Button>}
            </div>
            <form className="space-y-3" onSubmit={saveCustomer}>
              <label className="block text-sm font-medium text-slate-700">
                Name
                <Input className="mt-1" placeholder="Customer name" value={customerForm.name} minLength={2} maxLength={100} onChange={(e: any) => setCustomerForm({ ...customerForm, name: e.target.value })} required />
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Phone
                <Input className="mt-1" placeholder="03001234567" value={customerForm.phone} minLength={10} maxLength={15} onChange={(e: any) => setCustomerForm({ ...customerForm, phone: e.target.value })} required />
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Email
                <Input className="mt-1" type="email" placeholder="customer@example.com" value={customerForm.email} onChange={(e: any) => setCustomerForm({ ...customerForm, email: e.target.value })} />
              </label>
              <Button type="submit" disabled={loading} className="w-full">{editingCustomerId ? <><Save size={16} />Update Customer</> : <><Plus size={16} />Create Customer</>}</Button>
            </form>
          </Card>
        </section>}

        {isBusinessUser && selectedBusinessId && <Card>
          <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Business Hours</h2>
              <p className="text-sm text-slate-500">Set availability and open/close time for each day.</p>
            </div>
            <Button onClick={saveBusinessHours} disabled={loading}><Check size={16} />Save Hours</Button>
          </div>
          <div className="space-y-3">
            {businessHours.map((hour) => (
              <div key={hour.day_of_week} className="grid gap-3 rounded-xl border border-slate-200 p-3 md:grid-cols-[110px_130px_1fr_1fr] md:items-center">
                <span className="font-medium text-slate-900">{hour.day_of_week}</span>
                <div className="grid grid-cols-2.5 rounded-xl border border-slate-200 bg-slate-100 p-1">
                  <button
                    type="button"
                    onClick={() => updateHourRow(hour.day_of_week, { is_open: false })}
                    className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition ${!hour.is_open ? 'bg-red-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
                  >
                    Closed
                  </button>
                  <button
                    type="button"
                    onClick={() => updateHourRow(hour.day_of_week, { is_open: true })}
                    className={`rounded-lg px-3 py-2 text-sm font-semibold transition ${hour.is_open ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
                  >
                    Available
                  </button>
                </div>
                <label className="block text-sm font-medium text-slate-700">
                  Open
                  <Input className="mt-1" type="time" disabled={!hour.is_open} value={hour.open_time} onChange={(e: any) => updateHourRow(hour.day_of_week, { open_time: e.target.value })} />
                </label>
                <label className="block text-sm font-medium text-slate-700">
                  Close
                  <Input className="mt-1" type="time" disabled={!hour.is_open} value={hour.close_time} onChange={(e: any) => updateHourRow(hour.day_of_week, { close_time: e.target.value })} />
                </label>
              </div>
            ))}
          </div>
        </Card>}

        <section className="grid gap-5 lg:grid-cols-2">
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">My Appointments</h2>
              <select 
                className="rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-500"
                onChange={(e) => { if (e.target.value) viewAppointment(e.target.value); }}
                value=""
              >
                <option value="">Select to View</option>
                {appointments.map((a) => (
                  <option key={a.id} value={a.id}>
                    {formatDateTime(a.start_time)} - {a.status}
                  </option>
                ))}
              </select>
            </div>
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-2 font-semibold">Date</th>
                    <th className="px-3 py-2 font-semibold">Service name</th>
                    <th className="px-3 py-2 font-semibold">Appointment time</th>
                    <th className="px-3 py-2 font-semibold">Current status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {appointments.map((a) => (
                    <tr key={a.id} className="bg-white">
                      <td className="px-3 py-3 text-slate-700">{formatDate(a.start_time)}</td>
                      <td className="px-3 py-3 font-medium text-slate-900">{getServiceName(a.service_id)}</td>
                      <td className="px-3 py-3 text-slate-700">{formatTime(a.start_time)} - {formatTime(a.end_time)}</td>
                      <td className="px-3 py-3">
                        <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700">{a.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!appointments.length && <p className="bg-white p-3 text-sm text-slate-500">No appointments yet.</p>}
            </div>
            <div className="hidden">
              {appointments.slice(0, 5).map((a) => (
                <div key={a.id} className="rounded-xl border border-slate-200 p-3 text-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <b className="capitalize">{a.status}</b><br />
                      {formatDateTime(a.start_time)} → {formatDateTime(a.end_time)}
                    </div>
                  </div>
                </div>
              ))}
              {!appointments.length && <p className="text-sm text-slate-500">No appointments yet.</p>}
            </div>
          </Card>

          {isBusinessUser && <Card>
            <h2 className="mb-4 text-lg font-semibold">Business Appointments</h2>
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-2 font-semibold">Date</th>
                    <th className="px-3 py-2 font-semibold">Service name</th>
                    <th className="px-3 py-2 font-semibold">Appointment time</th>
                    <th className="px-3 py-2 font-semibold">Current status</th>
                    {/* <th className="px-3 py-2 font-semibold">Actions</th> */}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {businessAppointments.map((a) => (
                    <tr key={a.id} className="bg-white align-top">
                      <td className="px-3 py-3 text-slate-700">{formatDate(a.start_time)}</td>
                      <td className="px-3 py-3 font-medium text-slate-900">{getServiceName(a.service_id)}</td>
                      <td className="px-3 py-3 text-slate-700">{formatTime(a.start_time)} - {formatTime(a.end_time)}</td>
                      <td className="px-3 py-3">
                        <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700">{a.status}</span>
                      </td>
                      {/* <td className="px-3 py-3">
                        <div className="flex flex-wrap gap-2">
                          <Button variant="secondary" onClick={() => viewAppointment(a.id)}>View</Button>
                          <Button variant="secondary" onClick={() => updateAppointmentStatus(a.id, 'confirm')}>Confirm</Button>
                          <Button variant="secondary" onClick={() => updateAppointmentStatus(a.id, 'complete')}>Complete</Button>
                          <Button variant="secondary" onClick={() => updateAppointmentStatus(a.id, 'noShow')}>No show</Button>
                        </div>
                      </td> */}
                    </tr>
                  ))}
                </tbody>
              </table>
              {!businessAppointments.length && <p className="bg-white p-3 text-sm text-slate-500">No business appointments for selected business.</p>}
            </div>
          </Card>}
        </section>

        {showAppointmentModal && selectedAppointment && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <Card className="w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Appointment Details</h2>
                <button onClick={() => { setShowAppointmentModal(false); setSelectedAppointment(null); }} className="text-slate-400 hover:text-slate-600">✕</button>
              </div>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="font-medium capitalize">{selectedAppointment.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Service Name:</span>
                  <span className="font-medium">{selectedAppointment.service?.name || getServiceName(selectedAppointment.service_id)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Business Name:</span>
                  <span className="font-medium">{selectedAppointment.business?.name || getBusinessName(selectedAppointment.business_id)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Start Time:</span>
                  <span className="font-medium">{formatDateTime(selectedAppointment.start_time)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">End Time:</span>
                  <span className="font-medium">{formatDateTime(selectedAppointment.end_time)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">User email:</span>
                  <span className="font-medium">{getAppointmentUserName(selectedAppointment)}</span>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                {selectedAppointment.status === 'pending' && (
                  <Button onClick={() => confirmAppointment(selectedAppointment.id)} disabled={loading}>
                    Confirm
                  </Button>
                )}
                <Button onClick={() => setShowAppointmentModal(false)}>Close</Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </main>
  );
}

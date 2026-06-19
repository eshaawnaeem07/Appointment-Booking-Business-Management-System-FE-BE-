import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customerApi } from '../services/customer_api';
import useBusinessStore from '../store/useBusinessStore';

const BusinessCustomerForm = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const { businessId } = useBusinessStore();
  const [customer, setCustomer] = useState({
    name: '',
    phone: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);

  useEffect(() => {
    if (customerId) {
      setIsEditMode(true);
      const fetchCustomer = async () => {
        setLoading(true);
        try {
          const response = await customerApi.getCustomerById(businessId, customerId);
          setCustomer(response.data);
        } catch (err) {
          setError("Failed to fetch customer details.");
          console.error("Error fetching customer:", err);
        } finally {
          setLoading(false);
        }
      };
      fetchCustomer();
    }
  }, [customerId, businessId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCustomer((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate email before sending
    if (!customer.email || customer.email.trim() === '') {
      setError("Email is required.");
      setLoading(false);
      return;
    }

    if (!businessId) {
      setError("Business ID is missing. Cannot save customer.");
      setLoading(false);
      return;
    }

    try {
      if (isEditMode) {
        await customerApi.updateCustomer(businessId, customerId, customer);
      } else {
        await customerApi.createCustomer(businessId, customer);
      }
      navigate('/dashboard/customers');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'create'} customer.`;
      setError(errorMsg);
      console.error(`Error ${isEditMode ? 'updating' : 'creating'} customer:`, err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEditMode) return <p>Loading customer details...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{isEditMode ? 'Edit Customer' : 'Add New Customer'}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            name="name"
            id="name"
            value={customer.name}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
          <input
            type="tel"
            name="phone"
            id="phone"
            value={customer.phone}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email <span className="text-red-500">*</span></label>
          <input
            type="email"
            name="email"
            id="email"
            value={customer.email}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {loading ? 'Saving...' : (isEditMode ? 'Update Customer' : 'Add Customer')}
        </button>
        <button
          type="button"
          onClick={() => navigate('/dashboard/customers')}
          className="ml-3 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
      </form>
    </div>
  );
};

export default BusinessCustomerForm;

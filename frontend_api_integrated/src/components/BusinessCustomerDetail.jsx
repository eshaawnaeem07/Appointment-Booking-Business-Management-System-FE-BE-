import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customerApi } from '../services/customer_api';
import useBusinessStore from '../store/useBusinessStore';

const BusinessCustomerDetail = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const { businessId } = useBusinessStore();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCustomer = async () => {
      if (!businessId) {
        setError("No business ID found.");
        setLoading(false);
        return;
      }
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
  }, [businessId, customerId]);

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this customer?")) {
      setLoading(true);
      try {
        await customerApi.deleteCustomer(businessId, customerId);
        navigate('/dashboard/customers');
      } catch (err) {
        setError("Failed to delete customer.");
        console.error("Error deleting customer:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  if (loading) return <p>Loading customer details...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;
  if (!customer) return <p>Customer not found.</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Customer Details</h1>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg p-4">
        <p><strong>Name:</strong> {customer.name}</p>
        <p><strong>Phone:</strong> {customer.phone}</p>
        <p><strong>Email:</strong> {customer.email}</p>
        <p><strong>Created At:</strong> {new Date(customer.created_at).toLocaleDateString()}</p>
        <div className="mt-4">
          <Link 
            to={`/dashboard/customers/edit/${customer.id}`} 
            className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded mr-2"
          >
            Edit
          </Link>
          <button 
            onClick={handleDelete} 
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Delete
          </button>
        </div>
      </div>
      <button
        onClick={() => navigate('/dashboard/customers')}
        className="mt-4 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Back to Customers
      </button>
    </div>
  );
};

export default BusinessCustomerDetail;

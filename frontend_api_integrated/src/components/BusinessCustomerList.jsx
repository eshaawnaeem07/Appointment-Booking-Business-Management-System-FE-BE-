import React, { useEffect, useState } from 'react';
import { customerApi } from '../services/customer_api';
import useBusinessStore from '../store/useBusinessStore';
import { Link } from 'react-router-dom';

const BusinessCustomerList = () => {
  const [customers, setCustomers] = useState([]);
  const { businessId } = useBusinessStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCustomers = async () => {
      if (!businessId) {
        setError("No business ID found. Please ensure your business is selected.");
        setLoading(false);
        return;
      }
      try {
        const response = await customerApi.getAllCustomers(businessId);
        setCustomers(response.data);
      } catch (err) {
        setError("Failed to fetch customers.");
        console.error("Error fetching customers:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, [businessId]);

  if (loading) return <p>Loading customers...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Business Customers</h1>
      <Link 
        to={`/dashboard/customers/new`} 
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4 inline-block"
      >
        Add New Customer
      </Link>
      {customers.length === 0 ? (
        <p>No customers found for this business.</p>
      ) : (
        <ul className="space-y-2">
          {customers.map((customer) => (
            <li key={customer.id} className="bg-gray-100 p-3 rounded shadow flex justify-between items-center">
              <div>
                <p className="font-semibold">{customer.name}</p>
                <p className="text-sm text-gray-600">{customer.email} | {customer.phone}</p>
              </div>
              <Link 
                to={`/dashboard/customers/${customer.id}`} 
                className="text-blue-500 hover:underline"
              >
                View Details
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default BusinessCustomerList;

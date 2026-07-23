import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import type { SidebarUser } from './Sidebar/types';

import Sidebar from './Sidebar/Sidebar';
import Header from './Header/Header';
import Footer from './Footer/Footer';

import './MainLayout.css';

const MainLayout: React.FC = () => {
    const [user, setUser] = useState<SidebarUser | undefined>();
    const navigate = useNavigate();

    useEffect(() => {
        api.get('/auth/me')
            .then((res) => {
                const data = res.data;
                setUser({
                    id: data.id,
                    name: data.full_name,
                    email: data.email,
                    designation: "System Administrator", // Default designation if not in API
                });
            })
            .catch(() => {
                // If it fails, let api interceptor handle redirect
            });
    }, []);

    const handleLogout = async () => {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                await api.post('/auth/logout', { refresh_token: refreshToken });
            }
        } catch (e) {
            console.error('Logout failed on backend:', e);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            sessionStorage.clear();
            navigate('/login');
        }
    };

    return (
        <div className="app-layout">
            <Header user={user} onLogout={handleLogout} />
            <div className="app-body">
                <Sidebar />
                <div className="app-main">
                    <div className="page-container">
                        <Outlet />
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
};

export default MainLayout;
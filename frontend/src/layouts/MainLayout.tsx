import React from 'react';
import { Outlet } from 'react-router-dom';

import Sidebar from './Sidebar/Sidebar';
import Header from './Header/Header';
import Footer from './Footer/Footer';

import './MainLayout.css';

const MainLayout: React.FC = () => {
    return (
        <div className="app-layout">
            <Header />
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
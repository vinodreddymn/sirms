import React, { useEffect, useState } from 'react';
import {
    Search,
    Bell,
    Settings,
    HelpCircle,
    UserCircle2,
    LogOut,
    User
} from 'lucide-react';

import { api } from '../../services/api';
import geeBeeLogo from '../../assets/images/geebee-logo.png';
import './Header.css';
import type { SidebarUser } from '../Sidebar/types';

interface HeaderProps {
    user?: SidebarUser;
    onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {

    const [projects,setProjects]=useState<any[]>([]);
    const [selectedProject,setSelectedProject]=useState("");

    useEffect(()=>{

        api.get('/common/projects?page_size=25')
        .then(res=>{
            const items=res.data.items||[];
            setProjects(items);
            if(items.length)
                setSelectedProject(items[0].id);
        });

    },[]);

    const initials = user?.name
        ?.split(" ")
        .map(n => n[0])
        .slice(0, 2)
        .join("")
        .toUpperCase() || "U";

    return(
<header className="app-header">
    <div className="header-left">
        <img src={geeBeeLogo} alt="" className="logo" />
        <div className="brand">
            <div className="title">SIRMS</div>
            <div className="subtitle">Security Infrastructure Resource Management System</div>
        </div>
    </div>

    <div className="header-search">
        <Search size={16}/>
        <input placeholder="Search assets, incidents, locations..." />
    </div>

    <div className="header-right">
        <button className="toolbar-button">
            <HelpCircle size={18}/>
        </button>

        <button className="toolbar-button notification">
            <Bell size={18}/>
            <span>3</span>
        </button>

        <button className="toolbar-button">
            <Settings size={18}/>
        </button>

        {user && (
            <div className="user-menu">
                <button className="user-avatar-btn">
                    {user.avatar ? (
                        <img src={user.avatar} alt={user.name} style={{ width: '32px', height: '32px', borderRadius: '50%' }} />
                    ) : (
                        <div className="user-avatar-initials">{initials}</div>
                    )}
                </button>
                
                <div className="user-dropdown">
                    <div className="user-dropdown-header">
                        <div className="user-dropdown-name">{user.name}</div>
                        <div className="user-dropdown-email">{user.email}</div>
                        <div className="user-dropdown-designation">{user.designation}</div>
                    </div>
                    <div className="user-dropdown-body">
                        <button className="user-dropdown-item">
                            <User size={16} /> My Profile
                        </button>
                        <button className="user-dropdown-item logout" onClick={onLogout}>
                            <LogOut size={16} /> Logout
                        </button>
                    </div>
                </div>
            </div>
        )}
    </div>
</header>
    );
}

export default Header;
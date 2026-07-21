import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
    LayoutDashboard, Building2, Boxes, AlertTriangle,
    Wrench, FileText, Package, PieChart, Settings,
    ChevronDown, ChevronRight
} from 'lucide-react';

import './Sidebar.css';

interface NavItem {
    label: string;
    path: string;
}

interface NavSection {
    id: string;
    label: string;
    icon: React.ReactNode;
    path?: string; // If it's a direct link
    items?: NavItem[]; // If it has sub-items
}

const Sidebar: React.FC = () => {
    const location = useLocation();
    const [expandedSection, setExpandedSection] = useState<string | null>('assets');

    const navigation: NavSection[] = [
        { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={16} />, path: '/' },
        {
            id: 'infrastructure', label: 'Infrastructure', icon: <Building2 size={16} />,
            items: [
                { label: 'Sites', path: '/infrastructure/sites' },
                { label: 'Buildings', path: '/infrastructure/buildings' },
                { label: 'Floors', path: '/infrastructure/floors' },
                { label: 'Locations', path: '/infrastructure' }
            ]
        },
        {
            id: 'assets', label: 'Assets', icon: <Boxes size={16} />,
            items: [
                { label: 'Asset Register', path: '/assets' },
                { label: 'Categories', path: '/assets/categories' },
                { label: 'Asset Models', path: '/assets/models' },
                { label: 'Asset Search', path: '/assets/search' }
            ]
        },
        {
            id: 'incidents', label: 'Incidents', icon: <AlertTriangle size={16} />,
            items: [
                { label: 'Incident Register', path: '/incidents' }
            ]
        },
        {
            id: 'maintenance', label: 'Maintenance', icon: <Wrench size={16} />,
            items: [
                { label: 'Preventive', path: '/maintenance/preventive' },
                { label: 'Corrective', path: '/maintenance/corrective' },
                { label: 'Work Orders', path: '/maintenance/work-orders' }
            ]
        },
        { id: 'daily-work-log', label: 'Daily Work Log', icon: <FileText size={16} />, path: '/daily-work-log' },
        { id: 'inventory', label: 'Inventory', icon: <Package size={16} />, path: '/stock' },
        { id: 'reports', label: 'Reports', icon: <PieChart size={16} />, path: '/reports' },
        {
            id: 'administration', label: 'Administration', icon: <Settings size={16} />,
            items: [
                { label: 'Master Data', path: '/master' },
                { label: 'Specifications', path: '/master/specifications' },
                { label: 'Position Templates', path: '/master/position-templates' }
            ]
        }
    ];

    const toggleSection = (id: string, path?: string) => {
        if (path) {
            setExpandedSection(id);
        } else {
            setExpandedSection(prev => prev === id ? null : id);
        }
    };

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {navigation.map(section => {
                    const isExpanded = expandedSection === section.id;
                    const isActiveDirect = section.path && (location.pathname === section.path || (section.path !== '/' && location.pathname.startsWith(section.path)));
                    
                    return (
                        <div key={section.id} className="sidebar-section">
                            {section.path ? (
                                <NavLink 
                                    to={section.path}
                                    className={`sidebar-header ${isActiveDirect ? 'active' : ''}`}
                                    onClick={() => toggleSection(section.id, section.path)}
                                >
                                    <span className="sidebar-icon">{section.icon}</span>
                                    <span className="sidebar-label">{section.label}</span>
                                </NavLink>
                            ) : (
                                <div 
                                    className={`sidebar-header ${isExpanded ? 'expanded' : ''}`}
                                    onClick={() => toggleSection(section.id)}
                                >
                                    <span className="sidebar-icon">{section.icon}</span>
                                    <span className="sidebar-label">{section.label}</span>
                                    <span className="sidebar-arrow">
                                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                                    </span>
                                </div>
                            )}

                            {section.items && isExpanded && (
                                <div className="sidebar-items">
                                    {section.items.map(item => {
                                        const isItemActive = location.pathname === item.path || (item.path !== '/' && location.pathname === item.path);
                                        return (
                                            <NavLink
                                                key={item.path}
                                                to={item.path}
                                                className={`sidebar-item ${isItemActive ? 'active' : ''}`}
                                            >
                                                {item.label}
                                            </NavLink>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    );
                })}
            </nav>
        </aside>
    );
};

export default Sidebar;

import React, { useEffect, useRef, useState } from 'react';
import {
    Search,
    Bell,
    Settings,
    HelpCircle,
    LogOut,
    User,
    ChevronDown,
    Monitor
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
    const [projects, setProjects] = useState<any[]>([]);
    const [selectedProject, setSelectedProject] = useState('');
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let isMounted = true;

        api.get('/common/projects?page_size=25')
            .then((res) => {
                if (!isMounted) return;

                const items = res.data.items || [];
                setProjects(items);

                if (items.length && !selectedProject) {
                    setSelectedProject(items[0].id);
                }
            })
            .catch(() => {
                if (!isMounted) return;
                setProjects([]);
            });

        return () => {
            isMounted = false;
        };
    }, [selectedProject]);

    useEffect(() => {
        const handlePointerDown = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };

        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener('mousedown', handlePointerDown);
        document.addEventListener('keydown', handleEscape);

        return () => {
            document.removeEventListener('mousedown', handlePointerDown);
            document.removeEventListener('keydown', handleEscape);
        };
    }, []);

    const initials = user?.name
        ?.split(' ')
        .map((n) => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase() || 'U';

    const selectedProjectName = projects.find((project) => project.id === selectedProject)?.name || 'Select project';

    return (
        <header className="app-header">
            <div className="header-left">
                <img src={geeBeeLogo} alt="SIRMS logo" className="logo" />
                <div className="brand">
                    <div className="title">SIRMS</div>
                    <div className="subtitle">Security Infrastructure Resource Management System</div>
                </div>
            </div>

            <div className="header-center">
                <div className="project-box">
                    <select
                        value={selectedProject}
                        onChange={(event) => setSelectedProject(event.target.value)}
                        aria-label="Select project"
                    >
                        {projects.length ? (
                            projects.map((project) => (
                                <option key={project.id} value={project.id}>
                                    {project.name}
                                </option>
                            ))
                        ) : (
                            <option value="">No projects available</option>
                        )}
                    </select>
                    <ChevronDown size={16} className="project-box-icon" />
                </div>

                <div className="environment">
                    <Monitor size={14} />
                    <span>{selectedProjectName}</span>
                </div>
            </div>

            <div className="header-search">
                <Search size={16} />
                <input placeholder="Search assets, incidents, locations..." />
            </div>

            <div className="header-right">
                <button className="toolbar-button" aria-label="Help">
                    <HelpCircle size={18} />
                </button>

                <button className="toolbar-button notification" aria-label="Notifications">
                    <Bell size={18} />
                    <span>3</span>
                </button>

                <button className="toolbar-button" aria-label="Settings">
                    <Settings size={18} />
                </button>

                {user && (
                    <div className={`user-menu ${isMenuOpen ? 'open' : ''}`} ref={menuRef}>
                        <button
                            className="user-avatar-btn"
                            onClick={() => setIsMenuOpen((value) => !value)}
                            aria-expanded={isMenuOpen}
                            aria-haspopup="menu"
                            aria-label="Open user menu"
                        >
                            {user.avatar ? (
                                <img src={user.avatar} alt={user.name} className="user-avatar-image" />
                            ) : (
                                <div className="user-avatar-initials">{initials}</div>
                            )}
                        </button>

                        <div className="user-dropdown" role="menu">
                            <div className="user-dropdown-header">
                                <div className="user-dropdown-name">{user.name}</div>
                                <div className="user-dropdown-email">{user.email}</div>
                                <div className="user-dropdown-designation">{user.designation}</div>
                            </div>
                            <div className="user-dropdown-body">
                                <button className="user-dropdown-item" onClick={() => setIsMenuOpen(false)}>
                                    <User size={16} /> My Profile
                                </button>
                                <button
                                    className="user-dropdown-item logout"
                                    onClick={() => {
                                        setIsMenuOpen(false);
                                        onLogout?.();
                                    }}
                                >
                                    <LogOut size={16} /> Logout
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;

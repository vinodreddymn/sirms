import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { ChevronDown, ChevronRight } from "lucide-react";


import type { SidebarSection } from "./types";

interface SidebarItemProps {
    section: SidebarSection;
    collapsed: boolean;
    expanded: boolean;
    onToggle: (id: string) => void;
}

const SidebarItem: React.FC<SidebarItemProps> = ({
    section,
    collapsed,
    expanded,
    onToggle,
}) => {
    const location = useLocation();

    const Icon = section.icon;

    const hasChildren =
        !!section.children && section.children.length > 0;

    const isDirectActive =
        !!section.path &&
        (
            location.pathname === section.path ||
            (
                section.path !== "/" &&
                location.pathname.startsWith(section.path)
            )
        );

    const hasActiveChild =
        hasChildren &&
        section.children!.some(child =>
            location.pathname.startsWith(child.path)
        );

    const active = isDirectActive || hasActiveChild;

    /**
     * Badge
     */
    const renderBadge = () => {

        if (!section.badge) return null;

        if (section.badge.count === undefined &&
            !section.badge.text)
            return null;

        return (

            <span
                className={`sidebar-badge ${section.badge.color ?? "blue"}`}
            >

                {section.badge.count ?? section.badge.text}

            </span>

        );

    };

    /**
     * Direct Navigation
     */

    if (!hasChildren && section.path) {

        return (

            <NavLink

                to={section.path}

                title={collapsed ? section.label : ""}

                className={({ isActive }) =>
                    `sidebar-header ${isActive ? "active" : ""} ${section.disabled ? "disabled" : ""}`
                }

            >

                <span className="sidebar-icon">

                    <Icon size={18} />

                </span>

                {

                    !collapsed &&

                    <>

                        <span className="sidebar-label">

                            {section.label}

                        </span>

                        {renderBadge()}

                    </>

                }

            </NavLink>

        );

    }

    /**
     * Expandable Menu
     */

    return (

        <div className="sidebar-group">

            <button

                type="button"

                className={`sidebar-header ${active ? "active" : ""} ${expanded ? "expanded" : ""}`}

                title={collapsed ? section.label : ""}

                onClick={() => onToggle(section.id)}

            >

                <span className="sidebar-icon">

                    <Icon size={18} />

                </span>

                {

                    !collapsed &&

                    <>

                        <span className="sidebar-label">

                            {section.label}

                        </span>

                        {renderBadge()}

                        <span className="sidebar-arrow">

                            {

                                expanded

                                    ?

                                    <ChevronDown size={16} />

                                    :

                                    <ChevronRight size={16} />

                            }

                        </span>

                    </>

                }

            </button>

            {

                !collapsed &&
                expanded &&
                hasChildren &&

                <div className="sidebar-items">

                    {

                        section.children!.map(child => (

                            <NavLink

                                key={child.id}

                                to={child.path}

                                className={({ isActive }) =>
                                    `sidebar-item ${isActive ? "active" : ""} ${child.disabled ? "disabled" : ""}`
                                }

                            >

                                {

                                    child.icon &&

                                    <span className="sidebar-item-icon">

                                        <child.icon size={15} />

                                    </span>

                                }

                                <span>

                                    {child.label}

                                </span>

                                {

                                    child.badge &&

                                    <span
                                        className={`sidebar-badge ${child.badge.color ?? "blue"}`}
                                    >

                                        {child.badge.count ?? child.badge.text}

                                    </span>

                                }

                            </NavLink>

                        ))

                    }

                </div>

            }

        </div>

    );

};

export default SidebarItem;
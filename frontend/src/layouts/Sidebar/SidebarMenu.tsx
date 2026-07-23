import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import SidebarItem from "./SidebarItem";
import { navigation } from "./navigation";

interface SidebarMenuProps {
    collapsed: boolean;
}

const SidebarMenu: React.FC<SidebarMenuProps> = ({
    collapsed,
}) => {

    const location = useLocation();

    const [expandedSection, setExpandedSection] =
        useState<string | null>(null);

    /**
     * Expand the section that contains the current route
     */
    useEffect(() => {

        if (collapsed) return;

        const activeSection = navigation.find(section => {

            if (!section.children) return false;

            return section.children.some(child =>
                location.pathname.startsWith(child.path)
            );

        });

        if (activeSection) {

            setExpandedSection(activeSection.id);

        } else {

            setExpandedSection(null);

        }

    }, [location.pathname, collapsed]);

    /**
     * Toggle submenu
     */
    const toggleSection = (id: string) => {

        if (collapsed) return;

        setExpandedSection(prev =>
            prev === id ? null : id
        );

    };

    return (

        <nav className="sidebar-nav">

            {

                navigation.map(section => (

                    <SidebarItem

                        key={section.id}

                        section={section}

                        collapsed={collapsed}

                        expanded={expandedSection === section.id}

                        onToggle={toggleSection}

                    />

                ))

            }

        </nav>

    );

};

export default SidebarMenu;
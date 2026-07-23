import React from "react";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

interface SidebarHeaderProps {
    collapsed: boolean;
    onToggle: () => void;
}

const SidebarHeader: React.FC<SidebarHeaderProps> = ({
    collapsed,
    onToggle
}) => {
    return (
        <div className="sidebar-top">

            {!collapsed && (
                <div className="sidebar-brand">

                    <div className="sidebar-brand-logo">
                        S
                    </div>

                    <div className="sidebar-brand-text">

                        <div className="sidebar-title">
                            SIRMS
                        </div>

                        <div className="sidebar-subtitle">
                            Asset Management
                        </div>

                    </div>

                </div>
            )}

            <button
                type="button"
                className="collapse-btn"
                onClick={onToggle}
                aria-label={
                    collapsed
                        ? "Expand Sidebar"
                        : "Collapse Sidebar"
                }
            >
                {
                    collapsed
                        ? <PanelLeftOpen size={18} />
                        : <PanelLeftClose size={18} />
                }
            </button>

        </div>
    );
};

export default SidebarHeader;
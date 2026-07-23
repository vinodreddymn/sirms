import type { LucideIcon } from "lucide-react";

/**
 * Badge shown beside a menu item
 */
export interface SidebarBadge {
    text?: string;
    count?: number;
    color?: "blue" | "green" | "orange" | "red";
}

/**
 * Child menu item
 */
export interface SidebarItem {

    id: string;

    label: string;

    path: string;

    icon?: LucideIcon;

    badge?: SidebarBadge;

    /**
     * Required permission
     * Example:
     * asset:view
     */
    permission?: string;

    disabled?: boolean;
}

/**
 * Top level navigation section
 */
export interface SidebarSection {

    id: string;

    label: string;

    icon: LucideIcon;

    /**
     * Direct page
     */
    path?: string;

    /**
     * Expandable menu
     */
    children?: SidebarItem[];

    badge?: SidebarBadge;

    permission?: string;

    disabled?: boolean;
}

/**
 * Logged in user
 */
export interface SidebarUser {

    id: string;

    name: string;

    designation: string;

    email: string;

    avatar?: string;
}

/**
 * Sidebar State
 */
export interface SidebarState {

    collapsed: boolean;

    mobileOpen: boolean;

    expandedSection: string | null;

}

/**
 * Authentication Information
 */
export interface AuthInfo {

    accessToken: string;

    refreshToken: string;

    user: SidebarUser;

}

/**
 * Role
 */
export interface UserRole {

    id: string;

    name: string;

    permissions: string[];

}
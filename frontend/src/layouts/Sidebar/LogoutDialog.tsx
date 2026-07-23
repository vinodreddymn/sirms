import React, { useEffect } from "react";
import {
    LogOut,
    X
} from "lucide-react";

interface LogoutDialogProps {

    open: boolean;

    loading?: boolean;

    onCancel: () => void;

    onConfirm: () => void;

}

const LogoutDialog: React.FC<LogoutDialogProps> = ({

    open,

    loading = false,

    onCancel,

    onConfirm

}) => {

    /**
     * ESC closes dialog
     */
    useEffect(() => {

        if (!open) return;

        const listener = (event: KeyboardEvent) => {

            if (event.key === "Escape") {

                onCancel();

            }

        };

        window.addEventListener("keydown", listener);

        return () => {

            window.removeEventListener("keydown", listener);

        };

    }, [open, onCancel]);

    if (!open) {

        return null;

    }

    return (

        <div

            className="logout-overlay"

            onClick={onCancel}

        >

            <div

                className="logout-dialog"

                role="dialog"

                aria-modal="true"

                aria-labelledby="logout-title"

                onClick={(e) => e.stopPropagation()}

            >

                {/* Close */}

                <button

                    className="logout-close"

                    onClick={onCancel}

                    disabled={loading}

                >

                    <X size={18} />

                </button>

                {/* Icon */}

                <div className="logout-icon">

                    <LogOut size={34} />

                </div>

                {/* Title */}

                <h2

                    id="logout-title"

                    className="logout-title"

                >

                    Logout

                </h2>

                {/* Message */}

                <p className="logout-message">

                    You are about to sign out from

                    <strong> SIRMS</strong>.

                </p>

                <p className="logout-subtitle">

                    Any unsaved changes may be lost.

                </p>

                {/* Buttons */}

                <div className="logout-actions">

                    <button

                        className="logout-btn cancel"

                        onClick={onCancel}

                        disabled={loading}

                    >

                        Cancel

                    </button>

                    <button

                        className="logout-btn confirm"

                        onClick={onConfirm}

                        disabled={loading}

                    >

                        {

                            loading

                                ? "Signing Out..."

                                : "Logout"

                        }

                    </button>

                </div>

            </div>

        </div>

    );

};

export default LogoutDialog;
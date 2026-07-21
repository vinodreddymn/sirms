import React from 'react';
import {
    Server,
    Database,
    ShieldCheck,
    Clock3
} from 'lucide-react';

import './Footer.css';

const Footer: React.FC = () => {

    return (

        <footer className="app-footer">

            {/* Left */}

            <div className="footer-left">

                <span>

                    © 2026 Gee Bee Network Pvt. Ltd.

                </span>

                <span className="divider"></span>

                <span>

                    SIRMS v1.0.0

                </span>

            </div>

            {/* Center */}

            <div className="footer-center">

                <div className="footer-status success">

                    <Server size={15} />

                    API Connected

                </div>

                <div className="footer-status success">

                    <Database size={15} />

                    PostgreSQL Connected

                </div>

                <div className="footer-status">

                    <ShieldCheck size={15} />

                    Secure

                </div>

            </div>

            {/* Right */}

            <div className="footer-right">

                <Clock3 size={15} />

                <span>

                    Last Sync : Just now

                </span>

            </div>

        </footer>

    );

};

export default Footer;
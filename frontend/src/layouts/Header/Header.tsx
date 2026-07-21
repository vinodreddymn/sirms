import React, { useEffect, useState } from 'react';
import {
    Search,
    Bell,
    Settings,
    HelpCircle,
    ChevronDown,
    FolderKanban,
    Server,
    UserCircle2
} from 'lucide-react';

import { api } from '../../services/api';
import geeBeeLogo from '../../assets/images/geebee-logo.png';
import './Header.css';

const Header: React.FC = () => {

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

    return(

<header className="app-header">

    <div className="header-left">

        <img
            src={geeBeeLogo}
            alt=""
            className="logo"
        />

        <div className="brand">

            <div className="title">
                SIRMS
            </div>

            <div className="subtitle">
                Security Infrastructure Resource Management System
            </div>

        </div>

    </div>



    <div className="header-search">

        <Search size={16}/>

        <input
            placeholder="Search assets, incidents, locations..."
        />

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

        <div className="user">

            <UserCircle2 size={28}/>

            <div>

                <strong>Administrator</strong>

                <small>System Admin</small>

            </div>

            <ChevronDown size={16}/>

        </div>

    </div>

</header>

    );

}

export default Header;
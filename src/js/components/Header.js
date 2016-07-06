/**
 * Applikation för bostadsproduktionsplanering.
 * Sidorubrik.
 * 
 * Peter Ahlström 2016
 */

import React from 'react';

export default class Header extends React.Component {
    
    render() {
        return (
            <div>
                <h2>{this.props.header} &nbsp;<span><small>{this.props.subHeader}</small></span></h2>
            </div>
        )
    }
}
import React from 'react';
import PropTypes from 'prop-types';
import { Route, Redirect } from 'react-router-dom';
export const ProtectedRoute = ({ component: Component, ...rest }) => (
<Route {...rest} render={props => (
    
!localStorage.getItem('user')
? <Component {...props} />
: <Redirect to={{ pathname: '/login', state: { from: props.location } }} />
)} />
)

ProtectedRoute.propTypes = {
    user: PropTypes.shape({}),
    location: PropTypes.shape({}),
    component: PropTypes.shape({}),
};


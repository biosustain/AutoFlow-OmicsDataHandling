import React from 'react';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { ProtectedRoute } from './protected-routes';
import DesignType from './pages/design-type';
import DesignGraph from './pages/graph';
import LoginPage from './pages/login-page'

function AppRoutes() {
    return (
    <Router>
        <Switch>
             <Route exact path="/" component={LoginPage} />
            <Route path="/register" component={DesignType} />
            <Route path="/design-graph" component={DesignGraph} />
        </Switch>
        
    </Router>
    );
    }
    export default AppRoutes;
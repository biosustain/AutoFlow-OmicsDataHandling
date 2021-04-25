import { Button, Layout } from 'antd';
import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Route, Switch
} from "react-router-dom";
import './App.css';
import LoginPage from './pages/login-page';
import HomePage from './pages/home-page';
import DesignType from './pages/design-type';


const { Header, Footer, Sider, Content } = Layout;

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={LoginPage} />
        <Route path="/home" component={HomePage} />
        <Route path="/register" component={DesignType} />
      </Switch>
    </Router>
  );
}

export default App;

import { Avatar, Breadcrumb, Button, Layout, Menu } from 'antd';
import SubMenu from 'antd/lib/menu/SubMenu';
import Title from 'antd/lib/typography/Title';
import React, { useState } from 'react';
import {
    BrowserRouter as Router, NavLink,
    Link, Route, Switch
} from "react-router-dom";
import SampleSubmission from './sample-submission';
import AppRoutes from '../routes'
const { Header, Footer, Sider, Content } = Layout;

function Home() {
    const [selectedPlayer, setSelectedPlayer] = useState('');
    const [visible, setVisible] = useState(false);
    const onSelect = name => {
        setSelectedPlayer(name);
        setVisible(true);
    }
    const ViewProfileButton = ({ name }) => {
        return <Button type='dashed' style={{ float: 'right' }} onClick={() => onSelect(name)}> View Full Profile</Button>
    }

    const onClose = () => setVisible(false);
    return (
        <div className="App">
            <Layout>
                <Header style={{ padding: 10 }}>
                    <Avatar style={{ float: 'right' }} src='./dp.png' />
                    <Title style={{ color: 'white' }} level={3}>AUTOFLOW</Title>
                </Header>
                <Layout>
                    <Sider>
                        <Menu
                            defaultSelectedKeys={['Dashboard']}
                            mode="inline"
                        >
                            <SubMenu
                                title={
                                    <span>

                                        <span>DoE Module</span>
                                    </span>
                                }
                            >

                                <Menu.Item><NavLink to="/design-type">Design-Type</NavLink></Menu.Item>
                                <Menu.Item><NavLink to="/design-graph">Design-Graph</NavLink></Menu.Item>
                                <Link to="/register" className="btn btn-link">Register</Link>

                            </SubMenu>
                        </Menu>
                    </Sider>
                    <Layout>
                        <Content style={{ padding: '0 50px' }}>
                            <Breadcrumb style={{ margin: '16px 0' }}>

                            </Breadcrumb>
                            <div style={{ background: '#fff', padding: 24, minHeight: 580 }}>

                                <Router>
                                    <Switch>
                                        <Route exact path="/home" component={SampleSubmission} />
                                    </Switch>
                                </Router>
                            </div>
                        </Content>
                        <Footer></Footer>
                    </Layout>
                </Layout>
            </Layout>
        </div>
    );
}

export default Home;

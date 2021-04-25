import React from 'react';
import { Link } from 'react-router-dom';
let baseUrl = 'https://5aef530697c5.ngrok.io';

class SampleSubmission extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            sampleModule: '',
            sampleSelect: '',
            sampleData: [],
            typeName: '',
            method: '',
            description: '',
            research_center: ''
        };

        this.sampleChange = this.sampleChange.bind(this);
        this.deleteSample = this.deleteSample.bind(this);
        this.clearSample = this.clearSample.bind(this);
        this.typeChange = this.typeChange.bind(this);
        this.methodChange = this.methodChange.bind(this);
        this.centerChange = this.centerChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleSampleModuleSubmit = this.handleSampleModuleSubmit.bind(this);
    }

    componentDidMount() {
        this.getSampleDataList();
    }

    clearSample() {
        this.setState({
            sampleModule: ''
        });
        console.log(this.state.sampleModule);
    }

    sampleChange(event) {
        this.setState({
            sampleSelect: event.target.value
        });
        console.log(event.target.value);
    }

    deleteSample(event) {
        console.log('sample selete', this.state.sampleSelect);
        const requestOptions = {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ Sample_id: this.state.sampleSelect })
        };
        fetch(`${baseUrl}/Sample_api`, requestOptions)
            .then((response) => {
                alert('Sample successfully deleted')
                this.getSampleDataList();
                response.json()
            } )
    }

    typeChange(event) {
        this.setState({
            typeName: event.target.value
        });
        console.log(event.target.value);
    }

    methodChange(event) {
        this.setState({
            method: event.target.value,
            description: 'auto_populated'
        });
    }

    centerChange(event) {
        this.setState({
            method: event.target.value
        });
        console.log(event.target.value);
    }

    handleSubmit(e) {
        e.preventDefault();
        const { data } = this.state;
        let obj = {
            typeName: this.state.typeName,
            method: this.state.method,
            description: this.state.description,
            research_center: this.state.research_center
        }
    }

    setSampleModuleInput(e) {
        this.setState({
            sampleModule: e
        });
    }

    handleSampleModuleSubmit(e) {
        e.preventDefault();
        console.log('sample name', this.state.sampleModule);
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ Sample_name: this.state.sampleModule })
        };
        fetch(`${baseUrl}/Sample_api`, requestOptions)
            .then(response => response.json())
            .then((data) => {
                alert(data.message)
                this.getSampleDataList();
            })
    }

    getSampleDataList(){
        fetch(`${baseUrl}/Sample_api`, {method: "GET"})
        .then(response => response.json())
        .then(data => {
             this.setState({
                 sampleData: data.Sample
             })
        })

    }

    render() {
        let optionTemplate = this.state.sampleData.map(v => (
            <option value={v.id}>{v.Sample_name}</option>
          ));
        return (
            <div className="container">
                <ul className="nav nav-tabs" role="tablist">
                    <li className="nav-item">
                        <a className="nav-link active" data-toggle="tab" href="#SampleModule">Sample Module</a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" data-toggle="tab" href="#sampleSubmission">Sample Submission</a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" data-toggle="tab" href="#other">other</a>
                    </li>
                </ul>

                {/* Sample Module Form */}
                <div className="tab-content">
                    <div id="SampleModule" className="container tab-pane active">
                        <div className="col-md-4 col-md-offset-3">
                            <h2>Sample Module</h2>
                            <form name="form" onSubmit={this.handleSampleModuleSubmit}>
                                <div className={'form-group'}>
                                    <label>Sample</label>
                                    <input type="text" onInput={e => this.setSampleModuleInput(e.target.value)} className="form-control" name="description" />
                                </div>

                                <div className="form-group">
                                    <button className="btn btn-primary">Add</button>
                                    <button type="button" onClick={this.clearSample} className="btn btn-light">Cancel</button>
                                </div>
                            </form>

                            <div className={'form-group'} >
                                <label htmlFor="sample" style={{ marginTop: '40px' }}>Sample List</label>
                                <select className="form-control" value={this.state.value}  onChange={this.sampleChange}>
                                <option disabled selected>Select Sample</option>
                                {optionTemplate}
                                </select>
                            </div>
                            <div className="form-group">
                                <button onClick={this.deleteSample} className="btn btn-danger">Delete</button>
                            </div>
                        </div>
                    </div>

                    {/* Sample Submission */}

                    <div id="sampleSubmission" className="container tab-pane fade">

                        <div className="col-md-4 col-md-offset-3">
                            <h2>Sample Submission</h2>
                            <form name="form" onSubmit={this.handleSubmit}>
                                <div className={'form-group'}>
                                    <label htmlFor="username">Sample Type</label>
                                    <select className="form-control" onChange={this.typeChange}>
                                        <option disabled selected>Select Sample Type</option>
                                        <option value="lime">Lime</option>
                                        <option value="coconut">Coconut</option>
                                        <option value="mango">Mango</option>
                                    </select>
                                </div>
                                <div className={'form-group'}>
                                    <label>Methodology</label>
                                    <select className="form-control" onChange={this.methodChange} >
                                        <option disabled selected>Select Methodology</option>
                                        <option value="method1">Method1</option>
                                        <option value="m2">m2</option>
                                        <option value="m3">m3</option>
                                    </select>
                                </div>
                                <div className={'form-group'}>
                                    <label htmlFor="password">Description</label>
                                    <input disabled type="text" value={this.state.description} className="form-control" name="description" />
                                </div>
                                <div className={'form-group'}>
                                    <label>Research Center</label>
                                    <select className="form-control" onChange={this.centerChange}>
                                        <option disabled selected>Select Research Center</option>
                                        <option value="center1">center1</option>
                                        <option value="center2">center2</option>
                                        <option value="center3">center3</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <button className="btn btn-primary">Submit</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div id="other" className="container tab-pane fade">
                        <h3>Other</h3>
                        {/* <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.</p> */}
                    </div>
                </div>
            </div>
        );
    }
}

export default SampleSubmission;
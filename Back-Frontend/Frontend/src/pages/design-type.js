import React, { Component } from 'react';
import {Treebeard} from 'react-treebeard';

const SubmitButton = (props) => {
  return <button style={{ 'color': "white" }} type="submit" class="btn btn-success">Save</button>
}

const data = {
  name: 'Metabolic-Process',
  toggled: true,
  children: [
      {
          id: 'GO:0000001',
          name: 'Mitochondrion inheritance',
          namespace: 'biological_process',
          def: "The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton.[GOC:mcc, PMID:10873824, PMID:11389764]",
          synonym: "mitochondrial inheritance",
          children: [
              { name: 'Organelle inheritance', is_a: 'GO:0048308' },
              { name: 'Mitochondrion distribution',is_a: 'GO:0048311' }
          ]
      },
      {  
          id: 'GO:0000002',
          name: 'Mitochondrial genome maintenance',
          namespace: 'biological_process',
          def: "The maintenance of the structure and integrity of the mitochondrial genome; includes replication and segregation of the mitochondrial chromosome. [GOC:ai, GOC:vw]",
          is_a: 'GO:0007005'
      },
      {
        id: 'GO:0000003',
        name: 'reproduction',
        namespace: 'biological_process',
        alt_id: 'GO:0019952',
        alt_id: 'GO:0050876',
        def: "The production of new individuals that contain some portion of genetic material inherited from one or more parent organisms. [GOC:go_curators, GOC:isa_complete, GOC:jl, ISBN:0198506732]",
        is_a: 'GO:0008150'

      },
      {
        id: 'GO:0048308',
        name: 'organelle inheritance',
        namespace: 'biological_process',
        def: "The partitioning of organelles between daughter cells at cell division.",
      },
      {
        id: 'GO:0048311',
       name: 'mitochondrion distribution',
       namespace: 'biological_process',
      def: "Any process that establishes the spatial arrangement of mitochondria between and within cells.",
      is_a: 'GO:0007005',
      is_a: 'GO:0051646'
      }
  ]
};



class DesignType extends Component {
  constructor(props) {
    super(props);
    this.state = {
       value: '',
       data: data,
       clickedData : {}
       };
       this.onToggle = this.onToggle.bind(this);
       
  }

  handleChange = (event) => {
    this.setState({ value: event.target.value });
  }

  handleSubmit = (event) => {
    // alert('a name was subbed: ' + this.state.value);
    event.preventDefault();
  }

  onToggle(node, toggled){
    const {cursor, data} = this.state;
    if (cursor) { 
        this.setState(() => ({cursor, active: false}));
    }
    let a = this.state.data.children.filter((item)=>{
           return item.id ==  node.is_a
    })

    if(a.length == 0){
      this.setState(() => ({clickedData:  node}));
    } else {
      this.setState(() => ({clickedData:  a[0]}));
    }
    node.active = true;
    if (node.children) { 
        node.toggled = toggled; 
    }
   
    this.setState(() => ({cursor: node, data: Object.assign({}, data)}));
}

  render() {
    const {data} = this.state;
    return (
      <form onSubmit={this.handleSubmit}>
        <div className='row'>
          <div className='col-4'></div>
          <div className='col-4'>
          <div className="input-group">
          <input type="text" placeholder="Search" value={this.state.value} onChange={this.handleChange} />
          <div className="input-group-append">
            <button className="btn btn-success" type="submit">Go</button>
          </div>
          </div>
          </div>
          <div className='col-4'></div>
        </div>
        { this.state.value === 'm' &&
            <div className='row' style={{height:'500px', width: '100%', marginTop: '20px', border: '1px solid black'}}>
            <div className='col-4'  style={{height:'500px', width: '100%', border: '1px solid black'}}>
          <h5>Metabolic Process</h5>
            <Treebeard
                    data={data}
                    onToggle={this.onToggle}
                />
            </div>
            <div className='col-8'>
              {this.state.clickedData && this.state.clickedData.name &&
              <div>
              <h3>{this.state.clickedData.name}</h3>
              <p>{this.state.clickedData.def}</p>
              </div>
            }
            </div>
            </div>
          
        }
      
      </form>
    );
  }

}

export default DesignType;





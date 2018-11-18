import './index.css';

import * as serviceWorker from './serviceWorker';

import App, {BinApp} from './App';
import React, {Fragment} from 'react';

import ReactDOM from 'react-dom';

class Base extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      component: 'home'
    }
    this.switchComponent = this
      .switchComponent
      .bind(this);
  }

  switchComponent(component) {
    this.setState({component: component})
  }

  render() {
    return (
      <Fragment>
        {this.state.component === 'home'
          ? <App switchComponent={this.switchComponent}/>
          : <BinApp switchComponent={this.switchComponent}/>}
      </Fragment>
    )
  }
}

ReactDOM.render(
  <Base/>, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls. Learn
// more about service workers: http://bit.ly/CRA-PWA

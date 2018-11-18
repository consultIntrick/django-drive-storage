import './App.css';

import React, {Component, Fragment} from 'react';

import axios from 'axios';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      url: '/store/home/',
      value: '',
      selectedFile: null,
      loaded: 0,
      search: '',
      folders: [],
      files: [],
      domain: 'http://localhost:8000'
    };
  }

  folder = event => {
    this.setState({value: event.target.value});
    console.log(this.state.value);
  };

  file = event => {
    this.setState({
      selectedFile: event.target.files[0],
      loaded: 0
    }, () => {
      this.addFile();
    });
  };

  navigate = (event, url) => {
    this.setState({
      url: url
    }, () => {
      this.drive();
    });
  }

  addFile = () => {
    const data = new FormData();
    data.append('data', this.state.selectedFile, this.state.selectedFile.name);
    let url = this.state.domain + this.state.url;
    axios
      .post(url, data)
      .then(res => {
        console.log(res.statusText);
        this.setState({
          files: [
            ...this.state.files,
            res.data
          ]
        });
      })
  }

  deleteFolder = (event, url) => {
    url = this.state.domain + url
    axios
      .delete(url)
      .then(res => {
        console.log(res.statusText);
        this.componentDidMount();
      })
  }

  addFolder = () => {
    const data = new FormData();
    let url = this.state.domain + this.state.url;
    data.append('name', this.state.value);
    axios
      .post(url, data)
      .then(res => {
        console.log(res.statusText)
        this.setState({
          folders: [
            ...this.state.folders,
            res.data
          ]
        });
      })
  }

  drive = () => {
    let url = this.state.domain + this.state.url;
    axios
      .get(url)
      .then(res => {
        console.log(res.data);
        this.setState({files: res.data.files, folders: res.data.folders});
      })
  }

  componentDidMount = () => {
    this.drive();
  }

  render() {
    const files = this.state.files;
    const folders = this.state.folders;
    return (
      <Fragment>
        <nav className="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
          <input
            className="form-control form-control-dark w-100"
            type="text"
            onChange={(e) => this.search(e)}
            placeholder="Search"
            aria-label="Search"/>
        </nav>

        <div className="container-fluid">
          <div className="row">
            <nav className="col-md-2 d-none d-md-block bg-light sidebar">
              <div className="sidebar-sticky">
                <ul className="nav flex-column">
                  <li className="nav-item">
                    <a className="nav-link active" href="#">
                      <span data-feather="home"></span>
                      Home
                      <span className="sr-only">(current)</span>
                    </a>
                  </li>
                  <li className="nav-item">
                    <a
                      className="nav-link"
                      href="#"
                      onClick={(e) => this.props.switchComponent('bin')}>
                      <span data-feather="file"></span>
                      Bin
                    </a>
                  </li>
                </ul>
              </div>
            </nav>
            <main role="main" className="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4 row">
              <h5
                className="col-md-12"
                style={{
                "marginBottom": "30px"
              }}>Drive</h5>
              <h6 className="col-md-12">Manage Files/Folders</h6>
              <div
                className="col-md-2"
                style={{
                "marginBottom": "30px"
              }}>
                <div
                  style={{
                  width: "100%",
                  position: "relative",
                  cursor: "pointer"
                }}>
                  <button
                    className="btn btn-primary"
                    style={{
                    display: "inline-block",
                    width: "100%",
                    cursor: "pointer"
                  }}>
                    Add file
                  </button>
                  <input
                    type="file"
                    name="file"
                    onChange={(e) => this.file(e)}
                    style={{
                    position: "absolute",
                    top: "0",
                    right: "0",
                    opacity: "0",
                    width: "100%",
                    height: "100%",
                    cursor: "pointer"
                  }}/>
                </div>
              </div>
              <div
                className='col-md-5'
                style={{
                "marginBottom": "30px"
              }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter folder name"
                  value={this.state.value}
                  onChange={(e) => this.folder(e)}/>
              </div>
              <div
                className='col-md-2'
                style={{
                "marginBottom": "30px"
              }}>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={(e) => this.addFolder(e)}>Add Folder</button>
              </div>
            </main>
            <main role="main" className="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4 row">
              <h6
                className="col-md-12"
                style={{
                "marginBottom": "20px"
              }}>Folders</h6>
              {!folders.length && <p style={{
                'paddingLeft': '15px'
              }}>No folders present in this folder</p>}
              {folders.map((folder) => <div
                className="col-md-2"
                key={folder.id}
                style={{
                "marginBottom": "30px"
              }}>
                <button
                  className="btn btn-lg btn-outline-success"
                  style={{
                  "width": "100%",
                  "overflow": "hidden",
                  'borderBottomLeftRadius': '0',
                  'borderBottomRightRadius': '0'
                }}
                  onClick={(e) => this.navigate(e, folder.url)}>{folder.name}</button>
                <div
                  className="btn btn-success"
                  style={{
                  'padding': '0',
                  'borderTopLeftRadius': '0',
                  'borderTopRightRadius': '0',
                  'width': '100%'
                }}>
                  <a
                    style={{
                    'padding': '15px'
                  }}
                    onClick={(e) => this.deleteFolder(e, folder.delete_url)}>delete</a>
                </div>
              </div>)}
              <h6
                className="col-md-12"
                style={{
                "marginBottom": "20px"
              }}>Files</h6>
              {!files.length && <p style={{
                'paddingLeft': '15px'
              }}>No files present in this folder</p>}
              {files.map((file) => <div
                className="col-md-12"
                key={file.id}
                style={{
                "marginBottom": "30px"
              }}>
                <a href={this.state.domain + file.url}>{file.name}</a>
              </div>)}
            </main>
          </div>
        </div>
      </Fragment>
    );
  }
}

export class BinApp extends Component {
  constructor(props) {
    super(props);
    this.state = {
      url: '/store/bin/',
      value: '',
      selectedFile: null,
      loaded: 0,
      search: '',
      folders: [],
      files: [],
      domain: 'http://localhost:8000'
    };
  }

  folder = event => {
    this.setState({value: event.target.value});
    console.log(this.state.value);
  };

  file = event => {
    this.setState({
      selectedFile: event.target.files[0],
      loaded: 0
    }, () => {
      this.addFile();
    });
  };

  navigate = (event, url) => {
    this.setState({
      url: url
    }, () => {
      this.drive();
    });
  }

  restoreFolder = (event, url) => {
    url = this.state.domain + url
    axios
      .delete(url)
      .then(res => {
        console.log(res.statusText);
        this.componentDidMount();
      })
  }

  drive = () => {
    let url = this.state.domain + this.state.url;
    axios
      .get(url)
      .then(res => {
        console.log(res.data);
        this.setState({files: res.data.files, folders: res.data.folders});
      })
  }

  componentDidMount = () => {
    this.drive();
  }

  render() {
    const files = this.state.files;
    const folders = this.state.folders;
    return (
      <Fragment>
        <nav className="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
          <input
            className="form-control form-control-dark w-100"
            type="text"
            onChange={(e) => this.search(e)}
            placeholder="Search"
            aria-label="Search"/>
        </nav>

        <div className="container-fluid">
          <div className="row">
            <nav className="col-md-2 d-none d-md-block bg-light sidebar">
              <div className="sidebar-sticky">
                <ul className="nav flex-column">
                  <li className="nav-item">
                    <a
                      className="nav-link"
                      href="#"
                      onClick={(e) => this.props.switchComponent('home')}>
                      <span data-feather="home"></span>
                      Home
                      <span className="sr-only">(current)</span>
                    </a>
                  </li>
                  <li className="nav-item">
                    <a className="nav-link active" href="#">
                      <span data-feather="file"></span>
                      Bin
                    </a>
                  </li>
                </ul>
              </div>
            </nav>
            <main role="main" className="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4 row">
              <h5
                className="col-md-12"
                style={{
                "marginBottom": "30px"
              }}>Drive</h5>
              <h6 className="col-md-12">Bin</h6>
            </main>
            <main role="main" className="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4 row">
              <h6
                className="col-md-12"
                style={{
                "marginBottom": "20px"
              }}>Folders</h6>
              {!folders.length && <p style={{
                'paddingLeft': '15px'
              }}>No folders present in this folder</p>}
              {folders.map((folder) => <div
                className="col-md-2"
                key={folder.id}
                style={{
                "marginBottom": "30px"
              }}>
                <button
                  className="btn btn-lg btn-outline-success"
                  style={{
                  "width": "100%",
                  "overflow": "hidden",
                  'borderBottomLeftRadius': '0',
                  'borderBottomRightRadius': '0'
                }}
                  onClick={(e) => this.navigate(e, folder.url)}>{folder.name}</button>
                <div
                  className="btn btn-success"
                  style={{
                  'padding': '0',
                  'borderTopLeftRadius': '0',
                  'borderTopRightRadius': '0',
                  'width': '100%'
                }}>
                  <a
                    style={{
                    'padding': '15px'
                  }}
                    onClick={(e) => this.restoreFolder(e, folder.restore_url)}>Restore</a>
                </div>
              </div>)}
              <h6
                className="col-md-12"
                style={{
                "marginBottom": "20px"
              }}>Files</h6>
              {!files.length && <p style={{
                'paddingLeft': '15px'
              }}>No files present in this folder</p>}
              {files.map((file) => <div
                className="col-md-12"
                key={file.id}
                style={{
                "marginBottom": "30px"
              }}>
                <a href={this.state.domain + file.url}>{file.name}</a>
              </div>)}
            </main>
          </div>
        </div>
      </Fragment>
    );
  }
}

export default App;

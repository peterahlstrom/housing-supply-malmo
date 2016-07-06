/**
 * Applikation för bostadsproduktionsplanering.
 * Komponent för redigering av handläggare.
 * 
 * Peter Ahlström 2016
 */

import React from 'react';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import Slider from 'rc-slider';

export default class Admin extends React.Component {
	constructor() {
		super();
	}

	insertRowInDatabase(row) {
		const self = this;
		const url = config.insert_person_url;

		$.ajax({
			url: url,
			type: 'POST',
			data: JSON.stringify(row),
			contentType: 'application/json; charset=utf-8',
			success: function(resp){
				console.log('insert row success')
				console.log(resp);
				self.props.getListItems();
		    },
		    error: function(status, error) {
		    	console.error(status, error);
		    }
		});
	}

	deleteRowInDatabase(id) {
		const self = this;
		const url = config.delete_person_url;
		const postData = {id: id[0]};

		$.ajax({
			url: url,
			type: 'POST',
			data: JSON.stringify(postData),
			contentType: 'application/json; charset=utf-8',
			success: function(resp){
				console.log('delete row success')
				console.log(resp);

		    },
		    error: function(status, error) {
		    	console.error(status, error);
		    }
		});
	}

	render() {

		const tableOptions = {
			sortName: 'namn',
			sortOrder: 'asc',
            afterInsertRow: this.insertRowInDatabase.bind(this),
            afterDeleteRow: this.deleteRowInDatabase.bind(this),
		}

		const selectRowProp = {
		  mode: "checkbox", 
		  clickToSelect: true
		};

		return (
			<div>
				<h2>Redigera handläggare</h2>
				<div class="fifteen">
					<BootstrapTable data={this.props.data} 
							options={tableOptions}
							insertRow={true}
							deleteRow={true}
							deleteBtnDisabled={false}
							selectRow={selectRowProp}
							height={(window.innerHeight - 200).toString()}
							ref='table3' 
							striped={true} 
							hover={true} 
							search={false} 
							condensed={true}
							key="id" >
								<TableHeaderColumn dataField="id" autoValue={true} isKey={true} dataSort={false} hidden={true} >Id</TableHeaderColumn>
								<TableHeaderColumn dataField="namn" dataSort={false} hidden={false} >Handläggare</TableHeaderColumn>
					</BootstrapTable>
				</div>
			</div>
		)
	}
}
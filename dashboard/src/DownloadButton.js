import React from 'react';
import { styled } from '@material-ui/core/styles';
import { withStyles, makeStyles } from '@material-ui/core/styles';

import ToggleButton from '@material-ui/lab/ToggleButton';
import Button from '@material-ui/core/Button';


//Possible resource
//https://www.npmjs.com/package/react-csv

//learned something today: the text in a button is not encoded in a property value like background
//Two ways to do the same thing: styled and withStyles (in the comment below)

// Blob object for the content to be download
const csv_file = new Blob( //binary large object
  [ 'Vehicle,0367,Dex,IC15\n0.55155,19.258,3.4012,1.7465\n0.73538,1.4708,1.2869,2.2062\n2.436,0.36768,2.8496,1.5627' ],
  { type: 'text/csv' }
);


const buttonStyle = {
  background: 'linear-gradient(45deg, #56CCF2 30%, #2F80ED 90%)',
  //boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
  border: 0,
  borderRadius: 5,
  color: 'white',
  padding: '0 30px',
  height: 48,
  width: 160,
  //key 4 components to keep things in the middle, the top two allows the bottom two to work
  display: 'flex',
  flexDirection:'column',
  textAlign: 'center', //horizontal cetner
  justifyContent: 'center' // vetical center

}

const DownloadButton = (props) =>{
  const url = URL.createObjectURL(csv_file);
  return (
    <div className="parent">
      <a style = {buttonStyle} className="download" href={url} download= {props.filename} title = 'Export Records as CSV' >{props.text} </a>
    </div>

  );
};

export default DownloadButton;


/*

const HelperButton = styled(Button)({
  background: 'linear-gradient(45deg, #56CCF2 30%, #2F80ED 90%)',
  //boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
  border: 0,
  borderRadius: 5,
  color: 'white',
  height: 48,
  padding: '0 30px',
  display: 'inline-block'
});

export default function GradeintButton(props) {

  return (
      <HelperButton >
      {props.text}
      </HelperButton>
  );
}




const StyledButton = withStyles({
  root: {
    background: 'linear-gradient(45deg, #56CCF2 30%, #2F80ED 90%)',
    //boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
    border: 0,
    borderRadius: 5,
    color: 'white',
    height: 48,
    padding: '0 30px',
    display: 'inline-block'
  },
  label: {
    textTransform: 'capitalize',
  },
})(ToggleButton);

export default function GradientButton(props) {
  return <StyledButton>{props.text}</StyledButton>;
}
*/

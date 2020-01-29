// $Author: frederic $
// $Date: 2015/09/15 15:37:09 $
// $Id: standoffs.scad,v 1.4 2015/09/15 15:37:09 frederic Exp $

fourfortycleardiam=3.264;
fourfortytapdiam=2.438;
sixthirtytwotap=2.7051;
sixthirtytwoclear=3.7973;

module makestandoff(xloc,yloc,zloc,  //x,y,z location of center point in the bottom of cone.
                    outerdiameter,   //diameter, top of cone.
                    innerdiameter,   //hole diameter.
                    standofflength,  //height of the cone.
                    scalefac,        //scale factor for show.
         	        baseflarefac=1.5,//times between the diameter of bottom and top of cone.
   	                redrill=false,   //re drill.
	                toponly=true)    //
{
	echo("rendering standoff with redrill=",redrill);
	redrilloffset=toponly ? 0.0 : -0.5;
	redrilllengthfac=toponly ? 1.5: 2.0;
	if(!redrill)
	{
		translate([scalefac*xloc,scalefac*yloc,scalefac*zloc])
		{
			difference()
			{
				cylinder(r1=scalefac*baseflarefac*outerdiameter/2, //radius, bottom of cone.
					     r2=scalefac*outerdiameter/2, //radius, top of cone.
                         h=scalefac*standofflength);  //height of cone.
				cylinder(r=scalefac*innerdiameter/2, h=scalefac*standofflength);
			}
		}
	}
	else
	{
		//translate([scalefac*xloc,scalefac*yloc,redrilloffset*scalefac*zloc])
        translate([scalefac*xloc,scalefac*yloc,scalefac*zloc])
		{
			union()
			{
				cylinder(r=scalefac*innerdiameter/2, h=scalefac*(redrilllengthfac*standofflength));
			}
		}
	}
}

module makestandoffhole(xloc,yloc,zloc,innerdiameter,standofflength,scalefac)
{
	translate([scalefac*xloc,scalefac*yloc,scalefac*zloc])
	{
		translate([0,0,0])
		{
			union()
			{
				cylinder(r=scalefac*innerdiameter/2, h=scalefac*(standofflength));
				*translate([0,0,scalefac*(standofflength-innerdiameter/2)])
				{
					cylinder(r1=scalefac*innerdiameter/2,r2=scalefac*innerdiameter,
						h=scalefac*innerdiameter/2.0);
				}
			}
		}
	}
}


//example.    
//makestandoff(xloc=0,yloc=0,zloc=10,outerdiameter=8,innerdiameter=fourfortytapdiam,standofflength=10,
//             scalefac=1,baseflarefac=1.5,redrill=true,toponly=false);
    
// $Author: Yingwei Li $
// $Date: 2016/02/20 19:35:53 $
// $Id: mrilfoboard.scad,v 1.10 $

//----------------------------------------------------------------------
use <hollowbox.scad>
include <standoffs.scad>
use <holes.scad>
//----------------------------------------------------------------------
logo = 1;
scalefac=5;
wallthickness=2.5;
radius=30;
showboards=false;
//----------------------------------------------------------------------
// optical board and modpulse info.
boardclearnegx=0; 
boardclearnegy=0; 
boardclearnegz=0; 
boardclearposx=10;  //4.26 is spacing between teensy board and mod-pulse board.
boardclearposy=10;  //room for teensy port connector, one side is 0.5mm.
boardclearposz=10; // 10 for the epaper, 25 for the battery board
standoffheight=5;   //5: height from the botton of teensy board.
lidheight=5;        //5: height of lid.
// Set inner dimension of the hollow box. same with onelfoboard and oneekgboard.
xdim=140;
ydim=85; //72.0+5.7*2+1=84.4.
zdim=40; //5+24+5=34.
topbottomsplit=35;//24+5=29. the clear height of bottom part is 29.

// standoff info.
standoffod=7;
standoffid=fourfortytapdiam;

// top rim size.
rimthickness=2;
rimheight=2;
rimfudge=0.25;
//----------------------------------------------------------------------
//screw anchors.
sofudge=radius/8;
cornerholenegx=-boardclearnegx+sofudge;
cornerholeposx=xdim-boardclearnegx-sofudge;
cornerholenegy=-boardclearnegy+sofudge;
cornerholeposy=ydim-boardclearnegy-sofudge;
anchorod=12;
anchordepth=10.0;
countersinkdiam=7;
countersinkdepth=2;
// text parameters
textdepth=0.7;
logosize=6;
//----------------------------------------------------------------------
// battery location, x,y coordinate of middle point of battery.


//----------------------------------------------------------------------
// make this box.
module makethebox(istop)
{ 
    rotate([180*istop,0,0])
	{
        translate([0.0,0.0,-istop*(zdim)])
		{
		    scale([1/scalefac,1/scalefac,1/scalefac])
			{
			    difference()
				{
				    // here are all of the positive things
				    union()
					{ 
                        // first make the box itself. the z coordinate of bottom side is -2.5mm.
                        hollowbox(wallthickness,radius,
                                  xdim,ydim,zdim,
                                  boardclearnegx,
                                  boardclearnegy,
                                  boardclearnegz,
                                  topbottomsplit,
                                  scalefac);                        
                        if (istop != 0)  // if we need make a lid.
                        {
                            // add in the rim.                            
                            hollowbox(rimthickness,radius, //rimthickness is 2mm.
                                      xdim-2*rimthickness,ydim-2*rimthickness,zdim,
                                      boardclearnegx-rimthickness,  
                                      boardclearnegy-rimthickness,
                                      // this box is higher than old box 2+2-2.5=1.5mm. so we need
                                      // cut off them before finishing this lid.
                                      boardclearnegz-rimthickness,
                                      topbottomsplit,
                                      scalefac);
                        }
                        // make the screw anchors to hold the lid on.
                        for(xpos=[cornerholenegx,cornerholeposx,
                                 (cornerholenegx+cornerholeposx)/2.0])
                        {
                            for(ypos=[cornerholenegy,cornerholeposy])
                            {
                                makestandoff(xpos,ypos,topbottomsplit-anchordepth,
                                             anchorod,standoffid,anchordepth+zdim-topbottomsplit,
                                             scalefac,baseflarefac=1.0);
                            }
                        }                        
					}
                    // here are all of the negative things.
                    union()
                    {
                        if(istop==0)  // for jar.
                        {
                            // cut off lid (in top), to get box.
                            makerecthole(-boardclearnegx-1.5*wallthickness,
                                         -boardclearnegy-1.5*wallthickness,
                                         topbottomsplit,            // inner height is 29.
                                         3*wallthickness+xdim,                //3*2.5+142.29
                                         3*wallthickness+ydim,                //3*2.5+84.5
                                         3*wallthickness+zdim-topbottomsplit, //3*2.5+34-29
                                         scalefac);

// module makerecthole(xloc,yloc,zloc,xdim,ydim,zdim,scalefac)
                            screenholex = 89;
                            screenholey = 67;
                            makerecthole( (xdim /2 - screenholex/2) ,
                                          (ydim /2 - screenholey/2),
                                         -2*wallthickness,
                                         89,
                                         67,
                                         3*wallthickness,
                                         scalefac
                                        );

// power hole
 makerecthole(
 -5,
 30,
 17,
 10,15,10,scalefac
 
 )

                            //----------------------------------------------------------------------
                            // redrill anchor holes                            
                            for(xpos=[cornerholenegx,cornerholeposx,(cornerholenegx+cornerholeposx)/2.0])
                            {
                                for(ypos=[cornerholenegy,cornerholeposy])
                                {
                                    makestandoffhole(xpos,ypos,topbottomsplit-anchordepth,standoffid,
                                                     anchordepth+zdim-topbottomsplit,scalefac);
                                }
                            }
                        }
                        else   // for lid.
                        {
                            // cut off box (in bottom), to get lid. topbottomsplit is the height of 
                            // box,should cut off. so the inner height of lid is 34-29=5mm. rimheight 
                            // is the height of rim, should save, this is 2mm. so the total height of 
                            // lid is 2+5+2.5+1.5=11mm.
                            makerecthole(-boardclearnegx-1.5*wallthickness,
                                         -boardclearnegy-1.5*wallthickness,
                                         -boardclearnegz-1.5*wallthickness,
                                         3*wallthickness+xdim,
                                         3*wallthickness+ydim,
                                         topbottomsplit-rimheight+boardclearnegz+1.5*wallthickness,
                                         scalefac);
                            //----------------------------------------------------------------------
                            // cut off the wall, to get rim.
                            // for up rim.
                            makerecthole(-boardclearnegx-1.5*wallthickness,
                                         -boardclearnegy-1.5*wallthickness,
                                         -boardclearnegz+topbottomsplit-rimheight-rimfudge,
                                         1.5*wallthickness+rimfudge,
                                         3*wallthickness+ydim,
                                         rimheight+rimfudge,
                                         scalefac);
                            // for left rim.
                            makerecthole(-boardclearnegx-1.5*wallthickness,
                                         -boardclearnegy-1.5*wallthickness,
                                         -boardclearnegz+topbottomsplit-rimheight-rimfudge,
                                         3*wallthickness+xdim,
                                         1.5*wallthickness+rimfudge,
                                         rimheight+rimfudge,
                                         scalefac);                            
                            // for bottom rim.
                            makerecthole(-boardclearnegx+xdim-rimfudge,
                                         -boardclearnegy-1.5*wallthickness,
                                         -boardclearnegz+topbottomsplit-rimheight-rimfudge,
                                         1.5*wallthickness+rimfudge,
                                         3*wallthickness+ydim,
                                         rimheight+rimfudge,
                                         scalefac);
                            // for right rim.
                            makerecthole(-boardclearnegx-1.5*wallthickness,                        
                                         -boardclearnegy+ydim-rimfudge,       
                                         -boardclearnegz+topbottomsplit-rimheight-rimfudge,
                                         3*wallthickness+xdim,
                                         1.5*wallthickness+rimfudge,
                                         rimheight+rimfudge,
                                         scalefac);                                       
                            //----------------------------------------------------------------------
                            //cut off the excess standoff.
                            for(xpos=[cornerholenegx,cornerholeposx,(cornerholenegx+cornerholeposx)/2.0])
                            {
                                for(ypos=[cornerholenegy,cornerholeposy])
                                {
                                    makestandoff(xpos,ypos,topbottomsplit-rimheight,1.01*anchorod,
                                                 standoffid,rimheight,scalefac,baseflarefac=1.0);
                                }
                            }
                            //----------------------------------------------------------------------
                            // redrill anchor holes
                            for(xpos=[cornerholenegx,cornerholeposx,(cornerholenegx+cornerholeposx)/2.0])
                            {
                                for(ypos=[cornerholenegy,cornerholeposy])
                                {
                                    makestandoffhole(xpos,ypos,
                                            topbottomsplit-anchordepth,fourfortycleardiam,
                                            anchordepth+2*wallthickness+zdim-topbottomsplit,scalefac);
                                }
                            }
                            //----------------------------------------------------------------------
                            // countersink anchor holes
                            for(xpos=[cornerholenegx,cornerholeposx,(cornerholenegx+cornerholeposx)/2.0])
                            {
                                for(ypos=[cornerholenegy,cornerholeposy])
                                {
                                    makestandoffhole(xpos,ypos,zdim+wallthickness-countersinkdepth,
                                                     countersinkdiam,countersinkdepth,scalefac);
                                }
                            }
                            //----------------------------------------------------------------------
                            // put logo on top of box
                            if (logo==1) { 
                                translate([scalefac*(-boardclearnegx+xdim/2),
                                       scalefac*(-boardclearnegy+0.25*ydim-0.66*logosize),
                                       scalefac*(zdim+wallthickness-textdepth)])
                            {
                                rotate([0,0,0])
                                {
                                    linear_extrude(height=scalefac*textdepth)
                                    {
                                        text("Drucker 2020",size=scalefac*logosize,
                                             halign="center",valign="center");	
                                    }
                                }
                            } 
                           /*translate([scalefac*(-boardclearnegx+xdim/2),
                                       scalefac*(-boardclearnegy+0.25*ydim+0.66*logosize),
                                       scalefac*(zdim+wallthickness-textdepth)])
                            {
                                rotate([0,0,0])
                                {
                                    linear_extrude(height=scalefac*textdepth)
                                    {
                                        text("weather display",size=scalefac*logosize,
                                             halign="center",valign="center");	
                                    }
                                }
                            }*/ }
                            // now clean up the outside of the box.
                            hollowbox(wallthickness,radius,
                                       xdim,ydim,zdim,
                                       boardclearnegx,
                                       boardclearnegy,
                                       boardclearnegz,
                                       topbottomsplit,
                                       scalefac=5, redrill=true);                  
                        }
                    }
			    }
			}
		}
	}
}

////////////////////////////////////////////////////////////////////////////////////////
// make the bottom of the box
echo("");
echo("making the bottom of the box");
makethebox(0);

// make the top of the box
echo("");
echo("making the top of the box");
translate([0.0,-0.25*ydim,0])
{
	makethebox(1);
}
///////////////////////END/////////////////////////////////////////////////////////////	

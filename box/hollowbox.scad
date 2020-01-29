// $Author: frederic $
// $Date: 2015/10/02 19:26:53 $
// $Id: hollowbox.scad,v 1.6 2015/10/02 19:26:53 frederic Exp $

module maketab(xloc,yloc,zloc,tabsize,tabthickness,
               holediameter,scalefac,holeoffsetx=0,holeoffsety=0)
{
	translate([xloc*scalefac,yloc*scalefac,-zloc*scalefac])
	{
		difference()
		{
			cube([scalefac*tabsize, scalefac*tabsize, scalefac*tabthickness], center=false);
			translate([(holeoffsetx+tabsize/2.0)*scalefac,
                       (holeoffsety+tabsize/2.0)*scalefac,
                       (tabthickness/2.0)*scalefac])
			{
				cylinder(d=scalefac*holediameter, h=2.0*tabthickness*scalefac, center=true);
			}
		}
	}
}

module roundedBox(size, radius, sidesonly)
{
	rot = [ [0,0,0], [90,0,90], [90,90,0] ];
	if (sidesonly) 
    {
		cube(size - [2*radius,0,0], true);
		cube(size - [0,2*radius,0], true);
		for (x = [radius-size[0]/2, -radius+size[0]/2],
		     y = [radius-size[1]/2, -radius+size[1]/2]) 
        {
			translate([x,y,0]) cylinder(r=radius, h=size[2], center=true);
		}
	}
	else 
    {
		cube([size[0], size[1]-radius*2, size[2]-radius*2], center=true);
		cube([size[0]-radius*2, size[1], size[2]-radius*2], center=true);
		cube([size[0]-radius*2, size[1]-radius*2, size[2]], center=true);
		for (axis = [0:2]) 
        {
			for (x = [radius-size[axis]/2, -radius+size[axis]/2],
				 y = [radius-size[(axis+1)%3]/2, -radius+size[(axis+1)%3]/2]) 
            {
				rotate(rot[axis]) 
				translate([x,y,0]) 
				cylinder(h=size[(axis+2)%3]-2*radius, r=radius, center=true);
			}
		}
		for (x = [radius-size[0]/2, -radius+size[0]/2],
			 y = [radius-size[1]/2, -radius+size[1]/2],
			 z = [radius-size[2]/2, -radius+size[2]/2]) 
        {
			translate([x,y,z]) sphere(radius);
		}
	}
}

module hollowbox(wallthickness,    // wall thickness of box.
                 radius,
                 innerxdim,innerydim,innerzdim,  // x, y, z dimension of inner box.
                 boardclearnegx,   // the clear -x location of board.
                 boardclearnegy,   // the clear -y location of board.
                 boardclearnegz,   // the clear -z location of board.
                 topbottomsplit,
                 scalefac,         // scale factor.
                 redrill=false,    //redrill.
                 verbose=false)    //verbose.
{
	if(verbose)
	{
		echo("rendering hollowbox with redrill=",redrill);
	}
    // real inner box x,y,z dimension.
	// position the inside corner of the board at 0,0,0
	realinnerxdim=redrill ? 2.0*wallthickness+innerxdim : innerxdim;
	realinnerydim=redrill ? 2.0*wallthickness+innerydim : innerydim;
	realinnerzdim=redrill ? 2.0*wallthickness+innerzdim : innerzdim;
    // box x,y,z size.
	oboxxsize=redrill ? 5.0*wallthickness+innerxdim : 2.0*wallthickness+innerxdim;
	oboxysize=redrill ? 5.0*wallthickness+innerydim : 2.0*wallthickness+innerydim;
	oboxzsize=redrill ? 5.0*wallthickness+innerzdim : 2.0*wallthickness+innerzdim;
	difference()
	{
		translate([scalefac*(innerxdim/2.0-boardclearnegx),
			       scalefac*(innerydim/2.0-boardclearnegy),
			       scalefac*(innerzdim/2.0-boardclearnegz)])
		{
			roundedBox([scalefac*oboxxsize,scalefac*oboxysize,scalefac*oboxzsize], radius, false);
		}
		translate([scalefac*(innerxdim/2.0-boardclearnegx),
   			       scalefac*(innerydim/2.0-boardclearnegy),
			       scalefac*(innerzdim/2.0-boardclearnegz)])
		{
			roundedBox([scalefac*realinnerxdim,scalefac*realinnerydim,scalefac*realinnerzdim], 
                        radius, false);
		}
	}
}

//test.
/*
use <holes.scad>
wallthickness=2.5;
radius=30;
rffilterlen=19.96;
boardclearnegx=54.0; //romm for other board, ig:optical board, powercell board, etc.
//boardclearposx/2: is the x distance of outer board(DB9) to the inner wall of box.
boardclearposx=rffilterlen-2.0;	//=17.96. 2.0mm accounts for the offset of the shroud onto the board.
boardclearnegy=8.0;  //reserved room.
boardclearposy=6.0;  //boardclearposy/2: is the y distance of outer board to y axis. 
boardclearnegz=0;
boardclearposz=24;	 // the clear height of board. was 27 9/1/2015. 
boardxdim=71.12;     // x size of mod pulse board.
boardydim=76.2;      // y size of mod pulse board.
boardzdim=10.0;      // height from the botton of mod pulse board.
topbottomsplit=boardclearposz+5.0;   //24+5=29.
xdim=boardclearnegx+boardxdim+boardclearposx;  //54+71.12+19.96-2=143.08
ydim=boardclearnegy+boardydim+boardclearposy;  //8+76.2+6=90.2
zdim=boardclearnegz+boardzdim+boardclearposz;  //0+10+24=34
scalefac=5;
scale([1/scalefac,1/scalefac,1/scalefac])
{
    difference()
    {
        hollowbox(wallthickness,radius,xdim,ydim,zdim,
                  boardclearnegx,boardclearnegy,boardclearnegz,
                  topbottomsplit,scalefac,redrill=false);
        makerecthole(-boardclearnegx-1.5*wallthickness,   //-54-1.5*2.5=-57.75.
                     -boardclearnegy-1.5*wallthickness,   //-8-1.5*2.5=-11.75.
                     topbottomsplit,                      //29 
                     3*wallthickness+xdim,                //3*2.5+143.08
                     3*wallthickness+ydim,                //3*2.5+90.2
                     3*wallthickness+zdim-topbottomsplit, //3*2.5+34-29
                     scalefac); 
    }
}
*/

hollowbox(wallthickness=2.5,radius=30,innerxdim=123.56,innerydim=88.2,innerzdim=34,
          boardclearnegx=48.0,boardclearnegy=7.0,boardclearnegz=0,
          topbottomsplit=5.0,scalefac=5,redrill=true);

////////////////END/////////////////////////////////////////////////////////////////////

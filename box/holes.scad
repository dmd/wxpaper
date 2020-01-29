// $Author: frederic $
// $Date: 2015/09/15 15:29:45 $
// $Id: holes.scad,v 1.1 2015/09/15 15:29:45 frederic Exp $
bncholediameter=9.54;
bncdoffset=8/2;

module buttonhole(xloc,yloc,zloc,xdim,zdim,wallthickness,scalefac)
	{
	union()
		{
		translate([scalefac*(xloc),scalefac*(yloc),scalefac*zloc])
			{
			cube([scalefac*(xdim),scalefac*(2*wallthickness),scalefac*(zdim)]);
			}
		}
	}
// dimensions are NOT centered
module makerecthole(xloc,yloc,zloc,xdim,ydim,zdim,scalefac)
	{
	union()
		{
		translate([scalefac*(xloc),scalefac*(yloc),scalefac*zloc])
			{
			cube([scalefac*(xdim),scalefac*(ydim),scalefac*(zdim)]);
			}
		}
	}

// dimensions are NOT centered
module makeroundxhole(xloc,yloc,zloc,holediameter,length,scalefac)
	{
	union()
		{
		translate([scalefac*(xloc),scalefac*(yloc),scalefac*zloc])
			{
			rotate([0.0,90.0,0.0])
				{
				cylinder(r=scalefac*holediameter/2, h=scalefac*length);
				}
			}
		}
	}

module makeroundyhole(xloc,yloc,zloc,holediameter,length,scalefac)
	{
	union()
		{
		translate([scalefac*(xloc),scalefac*(yloc),scalefac*zloc])
			{
			rotate([0.0,90.0,90.0])
				{
				cylinder(r=scalefac*holediameter/2, h=scalefac*length);
				}
			}
		}
	}

module makebncxhole(xloc,yloc,zloc,length,scalefac,
	holediameter=bncholediameter,
	cutoutoffset=bncdoffset)
	{
	difference()
		{
		makeroundxhole(xloc,yloc,zloc,holediameter,length,scalefac);
		makerecthole(xloc,yloc+cutoutoffset,zloc-holediameter/2,length,5,holediameter,scalefac);
		}
	}

module makebncyhole(xloc,yloc,zloc,length,scalefac,
	holediameter=bncholediameter,
	cutoutoffset=bncdoffset)
	{
	difference()
		{
		makeroundyhole(xloc,yloc,zloc,holediameter,length,scalefac);
		makerecthole(xloc+cutoutoffset,yloc,zloc-holediameter/2,5,length,holediameter,scalefac);
		}
	}

*makebncxhole(0,0,10,5,10);
*makebncyhole(0,0,0,5,10);	
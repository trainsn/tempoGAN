#
# Flip surface mesh creation scene, note - saves & loads (ie plays back) meshes in UI mode
# 
from manta import *
import os
   
mantaMsg( "\nNote - this scene reads in particle data generated by, e.g., flip02_surface.py (set saveParts=True there). It does not perform any fluid simulation, only generate a nicer surface.\n" )


# === surface generation parameters ===

# input file 
partfile   = 'flipParts_%04d.uni' 
startFrame = 1
endFrame   = 1000
interval   = 1

# how much larger?
upres = 2.0

# output file name so that blender can directly read it...
meshfile = 'fluidsurface_final_%04d.bobj.gz' 

# resolution for level set / output mesh
refName = ("ref_" + (partfile % 0) ) 
gs = getUniFileSize(refName)
if gs.x<=0: 
	mantaMsg("Warning! File '%s' not found, cannot determine size...\n"%refName, 0)
	exit(1)

gs.x = int(gs.x*upres)
gs.y = int(gs.y*upres)
gs.z = int(gs.z*upres)
s = Solver(name='main', gridSize = gs , dim=3)

# kernel radius for surface creation
radiusFactor = 2.5

# triangle scale relative to cell size
#scale = 0.5

# counters
outCnt = 0
frame = startFrame


# prepare grids and particles
flags    = s.create(FlagGrid)
phi      = s.create(LevelsetGrid)
pp       = s.create(BasicParticleSystem) 
mesh     = s.create(Mesh)

# acceleration data for particle nbs
pindex = s.create(ParticleIndexSystem) 
gpi    = s.create(IntGrid)

# scene setup
flags.initDomain(boundaryWidth=0)
	
if 1 and (GUI):
	gui = Gui()
	gui.show()
	#gui.pause()


# main loop

while frame < endFrame:
	meshfileCurr = meshfile % outCnt 
	mantaMsg( "Frame %d " % frame )
	phi.setBound(value=0., boundaryWidth=1)

	# already exists?
	if (os.path.isfile( meshfileCurr )):
		mesh.load( meshfileCurr )

	else:
		# generate mesh; first read input sim particles
		if (os.path.isfile( partfile % frame )):
			pp.load( partfile % frame );
			
			# create surface
			gridParticleIndex( parts=pp , flags=flags, indexSys=pindex, index=gpi )
			#unionParticleLevelset( pp, pindex, flags, gpi, phi , radiusFactor ) # faster, but not as smooth
			averagedParticleLevelset( pp, pindex, flags, gpi, phi , radiusFactor , 1, 1 ) 

			phi.setBound(value=0., boundaryWidth=1)
			phi.createMesh(mesh)

			# beautify mesh, too slow right now!
			#subdivideMesh(mesh=mesh, minAngle=0.01, minLength=scale, maxLength=3*scale, cutTubes=False) 
			# perform smoothing
			#for iters in range(10):
				#smoothMesh(mesh=mesh, strength=1e-3, steps=10) 
				#subdivideMesh(mesh=mesh, minAngle=0.01, minLength=scale, maxLength=3*scale, cutTubes=True)

			# write output file:
			mesh.save( meshfileCurr )
		else:
			# stop playback for UI, reset
			if (GUI):
				gui.pause()
				outCnt = 0

	#gui.screenshot( 'flip03_%04d.png' % outCnt ); 
	outCnt += 1
	frame  += interval
	s.step()
	

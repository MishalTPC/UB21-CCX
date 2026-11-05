      program checkopen
      implicit none
      integer st
      real*8 d(6),a,iy,iz,j,ky,kz,ang
      d=0.d0
      d(1)=0.18d0
      d(2)=0.07d0
      d(3)=0.011d0
      d(4)=0.008d0
      st=5
      call compute_section_properties(dble(st),d,
     &  2.d11,0.3d0,a,iy,iz,j,ky,kz,ang)
      write(*,*) 'channel J:',j
      if(dabs(j/8.50334843085d-8-1.d0).gt.0.01d0)stop 2
      d=0.d0
      d(1)=0.07d0
      d(2)=0.07d0
      d(3)=0.008d0
      st=6
      call compute_section_properties(dble(st),d,
     &  2.d11,0.3d0,a,iy,iz,j,ky,kz,ang)
      write(*,*) 'angle J:',j
      if(dabs(j/2.1956646269d-8-1.d0).gt.0.01d0)stop 3
      write(*,*) 'OPEN SECTION TORSION PASS'
      end

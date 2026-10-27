! Standalone numerical regression for CalculiX local-1/local-2 conventions.
! Compile from repository root:
! gfortran -ffixed-line-length-none -c src/e_c3d_ubeam_utils.f -o /tmp/ubeam_utils.o
! gfortran validation/test_ccx_beam_axes.f90 /tmp/ubeam_utils.o -o /tmp/ccx_beam_axes
! /tmp/ccx_beam_axes
program test_ccx_beam_axes
  implicit none
  real(8) :: d(6), area, iyy, izz, torsion, ky, kz, angle
  real(8) :: area2, iy2, iz2, j2, ky2, kz2, angle2
  real(8) :: raw_area, raw_iy, raw_iz, raw_iyz, theta, pi
  real(8) :: rb(2),rh(2),ry(2),rz(2),cross_principal

  pi=4.d0*atan(1.d0)

  ! CCX RECT: first thickness is local 1/y; second is local 2/z.
  d=0.d0
  d(1)=0.1d0
  d(2)=0.2d0
  call compute_section_properties(1.d0,d,210.d9,0.3d0, &
       area,iyy,izz,torsion,ky,kz,angle)
  call assert_close('RECT area',area,0.02d0)
  call assert_close('RECT Iyy',iyy,0.1d0*0.2d0**3/12.d0)
  call assert_close('RECT Izz',izz,0.2d0*0.1d0**3/12.d0)
  if (iyy.le.izz) stop 'FAIL: expected strong axis about local 1'

  ! CCX BOX: t1=+1, t2=+2, t3=-1, t4=-2.
  ! A centred closed box has area / inertias equal to outer-inner.
  d=(/0.18d0,0.07d0,0.011d0,0.008d0,0.011d0,0.008d0/)
  call compute_section_properties(7.d0,d,210.d9,0.3d0, &
       area,iyy,izz,torsion,ky,kz,angle)
  call assert_close('BOX closed area',area, &
       0.18d0*0.07d0-(0.18d0-0.022d0)*(0.07d0-0.016d0))
  call assert_close('BOX closed Iyy',iyy, &
       (0.18d0*0.07d0**3-(0.18d0-0.022d0)*(0.07d0-0.016d0)**3)/12.d0)
  call assert_close('BOX closed Izz',izz, &
       (0.07d0*0.18d0**3-(0.07d0-0.016d0)*(0.18d0-0.022d0)**3)/12.d0)

  ! Opposite open walls have identical A, Iyy, Izz and torsion.
  ! Preserve the wall positions rather than converting them to CHAN.
  d=(/0.18d0,0.07d0,0.011d0,0.008d0,0.d0,0.008d0/)
  call compute_section_properties(7.d0,d,210.d9,0.3d0, &
       area,iyy,izz,torsion,ky,kz,angle)
  d=(/0.18d0,0.07d0,0.d0,0.008d0,0.011d0,0.008d0/)
  call compute_section_properties(7.d0,d,210.d9,0.3d0, &
       area2,iy2,iz2,j2,ky2,kz2,angle2)
  call assert_close('BOX mirrored area',area2,area)
  call assert_close('BOX mirrored Iyy',iy2,iyy)
  call assert_close('BOX mirrored Izz',iz2,izz)
  call assert_close('BOX mirrored J',j2,torsion)

  ! Asymmetric L-section: transformed product of inertia must vanish.
  ! Positive angle rotates local-1 (y) toward local-2 (z).
  d=0.d0
  d(1)=0.10d0
  d(2)=0.18d0
  d(3)=0.01d0
  call compute_section_properties(6.d0,d,210.d9,0.3d0, &
       area,iyy,izz,torsion,ky,kz,angle)
  rb=(/0.01d0,0.09d0/)
  rh=(/0.18d0,0.01d0/)
  ry=(/0.005d0,0.055d0/)
  rz=(/0.09d0,0.005d0/)
  call compute_composite_inertia(2,rb,rh,ry,rz, &
       raw_area,raw_iy,raw_iz,raw_iyz)
  theta=angle*pi/180.d0
  cross_principal=raw_iyz*cos(2.d0*theta)+ &
       0.5d0*(raw_iy-raw_iz)*sin(2.d0*theta)
  if (abs(cross_principal).gt.1.d-12) then
      write(*,*) 'FAIL: principal-axis product remains ', cross_principal
      stop 1
  endif
  call assert_close('L principal Iyy',iyy, &
       raw_iy*cos(theta)**2+raw_iz*sin(theta)**2- &
       2.d0*raw_iyz*sin(theta)*cos(theta))
  call assert_close('L principal Izz',izz, &
       raw_iy*sin(theta)**2+raw_iz*cos(theta)**2+ &
       2.d0*raw_iyz*sin(theta)*cos(theta))

  print *, 'PASS: CCX RECT/BOX axes and L principal rotation'
contains
  subroutine assert_close(name,actual,expected)
    character(*),intent(in) :: name
    real(8),intent(in) :: actual,expected
    if (abs(actual-expected)>max(1.d-12,1.d-8*abs(expected))) then
      write(*,*) 'FAIL: ',name,': ',actual,' expected ',expected
      stop 1
    endif
  end subroutine
end program

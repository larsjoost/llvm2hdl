library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.signed;
use ieee.numeric_std.resize;

package llvm_pkg is

  function conv_std_ulogic_vector (
    arg                 : integer;
    constant data_width : positive)
    return std_ulogic_vector;

  function conv_std_ulogic_vector (
    arg                 : std_ulogic_vector;
    constant data_width : positive)
    return std_ulogic_vector;

  function conv_std_ulogic_vector (
    arg                 : boolean;
    constant data_width : positive)
    return std_ulogic_vector;

end package llvm_pkg;

package body llvm_pkg is

  function conv_std_ulogic_vector (
    arg                 : integer;
    constant data_width : positive)
    return std_ulogic_vector is
  begin
    return std_ulogic_vector(to_signed(arg, data_width));
  end function conv_std_ulogic_vector;

  function conv_std_ulogic_vector (
    arg                 : std_ulogic_vector;
    constant data_width : positive)
    return std_ulogic_vector is
  begin
    return std_ulogic_vector(resize(signed(arg), data_width));
  end function conv_std_ulogic_vector;

  function conv_std_ulogic_vector (
    arg                 : boolean;
    constant data_width : positive)
    return std_ulogic_vector is
    variable result_v : std_ulogic_vector(0 to data_width - 1);
  begin
    if arg then
      result_v := (others => '1');
    else
      result_v := (others => '0');
    end if;
    return result_v;
  end function conv_std_ulogic_vector;

end package body llvm_pkg;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.signed;
use ieee.numeric_std.resize;

package llvm_pkg is

  type integer_array_t is array (natural range <>) of integer;

  function get(data : std_ulogic_vector; data_width: positive; index: natural := 0) 
  return std_ulogic_vector;

  function get(data : integer; data_width: positive) 
  return std_ulogic_vector;

  function get(data : integer_array_t; data_width: positive) 
  return std_ulogic_vector;

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
  
  function get(data : std_ulogic_vector; data_width: positive; index: natural := 0) 
  return std_ulogic_vector is
  alias x : std_ulogic_vector(0 to data'length - 1) is data;
  begin
    return x(index*data_width to (index + 1)*data_width - 1);
  end function get;

  function get(data : integer; data_width: positive) 
  return std_ulogic_vector is
  begin
    return std_ulogic_vector(to_signed(data, data_width));
  end function get;

  function get(data : integer_array_t; data_width: positive) 
    return std_ulogic_vector is
    constant c_data_width  : positive := data_width / data'length;
    variable x : std_ulogic_vector(0 to data_width - 1);
  begin
    for i in data'range loop
      x(i*c_data_width to (i+1)*c_data_width - 1) := std_ulogic_vector(to_signed(data(i), c_data_width));
    end loop;
    return x;
  end function get;

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

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.signed;
use ieee.numeric_std.unsigned;
use ieee.numeric_std.resize;

package llvm_pkg is

  type integer_array_t is array (natural range <>) of integer;

  constant c_integer_array_default : integer_array_t(0 to 0) := (others => 0);
  
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

  function to_std_ulogic_vector(arg : std_ulogic)
    return std_ulogic_vector;

  function to_std_ulogic_vector(arg : std_ulogic_vector)
    return std_ulogic_vector;

  end package llvm_pkg;

package body llvm_pkg is
  
  function get(data : std_ulogic_vector; data_width: positive; index: natural := 0) 
    return std_ulogic_vector is
    constant c_data_width : positive := data_width * (index + 1);
    variable x : std_ulogic_vector(c_data_width - 1 downto 0);
  begin
    x := std_ulogic_vector(resize(unsigned(data), c_data_width)); 
    return x((index + 1)*data_width - 1 downto index*data_width);
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

  function to_std_ulogic_vector(arg : std_ulogic)
    return std_ulogic_vector is
  variable x : std_ulogic_vector(0 to 0);
    begin
      x(0) := arg;
      return x;
    end function to_std_ulogic_vector;

  function to_std_ulogic_vector(arg : std_ulogic_vector)
    return std_ulogic_vector is
    begin
      return arg;
    end function to_std_ulogic_vector;
    
end package body llvm_pkg;

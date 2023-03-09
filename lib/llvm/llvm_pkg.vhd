library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.signed;
use ieee.numeric_std.unsigned;
use ieee.numeric_std.resize;

library ieee;
use ieee.float_pkg.float;
use ieee.float_pkg.to_float;
use ieee.float_pkg.float32;
use ieee.float_pkg.float64;
use ieee.float_pkg.float128;
use ieee.float_pkg.to_real;
use ieee.float_pkg.to_slv;

package llvm_pkg is

  type integer_array_t is array (natural range <>) of integer;

  constant c_integer_array_default : integer_array_t(0 to 0) := (others => 0);

  function get(data : std_ulogic_vector; data_width : positive; index : natural := 0)
    return std_ulogic_vector;

  function get(data : integer; data_width : positive)
    return std_ulogic_vector;

  function get(data : real; data_width : positive)
    return std_ulogic_vector;

  function get(data : integer_array_t; data_width : positive)
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

  function to_real (
    arg : std_ulogic_vector)
    return real;
  
end package llvm_pkg;

package body llvm_pkg is

  function get(data : std_ulogic_vector; data_width : positive; index : natural := 0)
    return std_ulogic_vector is
    constant c_data_width : positive := data_width * (index + 1);
    alias data_v          : std_ulogic_vector(0 to data'length - 1) is data;
    variable x            : std_ulogic_vector(c_data_width - 1 downto 0);
  begin
    if data'length < c_data_width then
      x := std_ulogic_vector(resize(unsigned(data), c_data_width));
    else
      x := data_v(0 to c_data_width - 1);
    end if;
    return x((index + 1)*data_width - 1 downto index*data_width);
  end function get;

  function get(data : integer; data_width : positive)
    return std_ulogic_vector is
  begin
    return std_ulogic_vector(to_signed(data, data_width));
  end function get;

  function get(data : real; data_width : positive)
    return std_ulogic_vector is
  begin
    return to_slv(to_float(data));
  end function get;

  function get(data : integer_array_t; data_width : positive)
    return std_ulogic_vector is
    constant c_data_width : positive := data_width / data'length;
    variable x            : std_ulogic_vector(0 to data_width - 1);
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

  function to_real (
    arg : std_ulogic_vector)
    return real is
  begin
    case arg'length is
      when 32 =>
        return to_real(float32(arg));
      when 64 =>
        return to_real(float64(arg));
      when 128 =>
        return to_real(float128(arg));
      when others =>
        --pragma synthesis_off
        report "Unsupported argument length = " & integer'image(arg'length) severity failure;
        --pragma synthesis_on
    end case;
    return 0.0;
  end function to_real;
  
end package body llvm_pkg;

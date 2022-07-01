library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.signed;
use ieee.numeric_std.resize;

package llvm_pkg is

  type integer_array_t is array (natural range <>) of integer;
  
  type memory_i32 is array (natural range <>) of std_ulogic_vector(0 to 31);

  function set_memory_i32 (
    data : integer_array_t)
    return memory_i32;
  
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

  function set_memory_i32 (
    data : integer_array_t)
    return memory_i32 is
    alias data_a : integer_array_t(0 to data'length - 1) is data;
    variable result_v : memory_i32(0 to data'length - 1);
  begin
    for i in 0 to data'length - 1 loop
      result_v(i) := std_ulogic_vector(to_signed(data_a(i), 32));
    end loop;
    return result_v;
  end function set_memory_i32;
  
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

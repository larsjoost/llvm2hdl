library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.numeric_std.shift_right;
use ieee.numeric_std.to_integer;
use ieee.numeric_std.unsigned;

entity llvm_ashr is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector;
    b       : in  std_ulogic_vector
    );
end entity llvm_ashr;

architecture rtl of llvm_ashr is

begin

  process (clk)
  begin
    if rising_edge(clk) then
      q       <= std_ulogic_vector(shift_right(unsigned(a), to_integer(unsigned(b))));
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;

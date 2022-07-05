library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_and is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector;
    b       : in  std_ulogic_vector
    );
end entity llvm_and;

architecture rtl of llvm_and is

begin

  process (clk)
  begin
    if rising_edge(clk) then
      q       <= a and b;
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;

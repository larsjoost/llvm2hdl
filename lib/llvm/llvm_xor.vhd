library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_xor is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector(0 to 0);
    a       : in  std_ulogic_vector(0 to 0);
    b       : in  std_ulogic_vector(0 to 0)
    );
end entity llvm_xor;

architecture rtl of llvm_xor is

begin

  process (clk)
  begin
    if rising_edge(clk) then
      q       <= a xor b;
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;

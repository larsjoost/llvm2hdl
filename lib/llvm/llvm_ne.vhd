library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_ne is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector(0 to 32 - 1);
    a       : in  std_ulogic_vector(0 to 32 - 1);
    b       : in  std_ulogic_vector(0 to 32 - 1)
    );
end entity llvm_ne;

architecture rtl of llvm_ne is

begin

  process (clk)
  begin
    if rising_edge(clk) then
      if a = b then
        q <= (others => '0');
      else
        q <= (others => '1');
      end if;
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_mul is
  generic (
    tag_width : positive := 1
    );
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector(0 to tag_width - 1) := (others => '0');
    tag_out : out std_ulogic_vector(0 to tag_width - 1);
    q       : out std_ulogic_vector(0 to 32 - 1);
    a       : in  std_ulogic_vector(0 to 32 - 1);
    b       : in  std_ulogic_vector(0 to 32 - 1)
    );
end entity llvm_mul;

architecture rtl of llvm_mul is

begin

  process (clk)
    variable x : std_ulogic_vector(63 downto 0);
  begin
    if rising_edge(clk) then
      x       := std_ulogic_vector(unsigned'(unsigned(a) * unsigned(b)));
      q       <= x(31 downto 0);
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;

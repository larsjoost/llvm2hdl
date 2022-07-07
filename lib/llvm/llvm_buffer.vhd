
library ieee;
use ieee.std_logic_1164.all;

entity llvm_buffer is
  port (
    clk      : in  std_ulogic;
    sreset   : in  std_ulogic;
    s_tag    : in  std_ulogic_vector;
    s_tvalid : in  std_ulogic;
    s_tready : out std_ulogic;
    s_tdata  : in  std_ulogic_vector;
    m_tvalid : out std_ulogic;
    m_tready : in  std_ulogic;
    m_tag    : out std_ulogic_vector;
    m_tdata  : out std_ulogic_vector
    );
end entity llvm_buffer;

architecture rtl of llvm_buffer is

begin

  s_tready <= m_tready or (not m_tvalid);

  process (clk)
  begin
    if rising_edge(clk) then
      if sreset = '1' then
        m_tvalid <= '0';
      else
        if m_tready = '1' then
          m_tvalid <= '0';
        end if;
        if s_tvalid = '1' and s_tready = '1' then
          m_tvalid <= '1';
        end if;
      end if;
    end if;
  end process;

  process (clk)
  begin
    if rising_edge(clk) then
      if s_tvalid = '1' and s_tready = '1' then
        m_tdata <= s_tdata;
        m_tag   <= s_tag;
      end if;
    end if;
  end process;

end architecture rtl;

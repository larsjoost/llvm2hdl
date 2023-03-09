library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_fcmp_ule is
  port (
    clk      : in  std_ulogic;
    sreset   : in  std_ulogic;
    a        : in  std_ulogic_vector;
    b        : in  std_ulogic_vector;
    s_tag    : in  std_ulogic_vector;
    s_tvalid : in  std_ulogic;
    s_tready : out std_ulogic;
    m_tvalid : out std_ulogic;
    m_tready : in  std_ulogic;
    m_tag    : out std_ulogic_vector;
    m_tdata  : out std_ulogic_vector);
end entity llvm_fcmp_ule;

library ieee;
use ieee.float_pkg.float32;
use ieee.float_pkg.to_float;
use ieee.float_pkg.to_slv;
use ieee.float_pkg.to_real;
use ieee.float_pkg."abs";

architecture rtl of llvm_fcmp_ule is

  constant c_data_width : positive := m_tdata'length;

  signal a_i : float32;
  signal b_i : float32;
  signal q_i : boolean;
  
  signal s_tdata_i : std_ulogic_vector(0 to c_data_width - 1);

begin

  a_i <= to_float(a);

  b_i <= to_float(b);

  q_i <= (abs(a_i) <= abs(b_i));
  
  s_tdata_i <= (others => '1') when (q_i) else (others => '0');

  llvm_buffer_1 : entity work.llvm_buffer(rtl)
    port map (
      clk      => clk,
      sreset   => sreset,
      s_tag    => s_tag,
      s_tvalid => s_tvalid,
      s_tready => s_tready,
      s_tdata  => s_tdata_i,
      m_tvalid => m_tvalid,
      m_tready => m_tready,
      m_tag    => m_tag,
      m_tdata  => m_tdata);

  --pragma synthesis_off

  process (clk) is
  begin 
    if rising_edge(clk) then
      if sreset = '1' then
        null;
      else
        if s_tvalid = '1' and s_tready = '1' then
          report "(" & real'image(to_real(a_i)) & " <= " & real'image(to_real(b_i)) & ") = " & boolean'image(q_i);
        end if;
      end if;
    end if;
  end process;
   
  --pragma synthesis_on
  
end architecture rtl;

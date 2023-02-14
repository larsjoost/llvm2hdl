library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_load is
  port (
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    a         : in  std_ulogic_vector;
    s_tvalid  : in  std_ulogic;
    s_tready  : out std_ulogic;
    s_tag     : in  std_ulogic_vector;
    m_tag     : out std_ulogic_vector;
    m_tvalid  : out std_ulogic;
    m_tready  : in  std_ulogic;
    m_tdata   : out std_ulogic_vector;
    m_araddr  : out std_ulogic_vector;
    m_arid    : out std_ulogic_vector;
    m_arvalid : out std_ulogic;
    m_arready : in  std_ulogic;
    m_rdata   : in  std_ulogic_vector;
    m_rvalid  : in  std_ulogic;
    m_rready  : out std_ulogic;
    m_rid     : in  std_ulogic_vector;
    m_awaddr  : out std_ulogic_vector;
    m_awid    : out std_ulogic_vector;
    m_awvalid : out std_ulogic;
    m_awready : in  std_ulogic;
    m_wready  : in  std_ulogic;
    m_wvalid  : out std_ulogic;
    m_wdata   : out std_ulogic_vector;
    m_wid     : out std_ulogic_vector;
    m_bready  : out std_ulogic;
    m_bvalid  : in  std_ulogic;
    m_bid     : in  std_ulogic_vector
    );
end entity llvm_load;

architecture rtl of llvm_load is

  constant c_id_width : positive := m_arid'length;
  constant c_id_size  : positive := 2 ** c_id_width;

  type tag_storage_t is array (0 to c_id_size - 1) of
    std_ulogic_vector(0 to s_tag'length - 1);

  signal tag_storage_i   : tag_storage_t;
  signal data_transfer_i : std_ulogic;
  signal id_i            : natural range 0 to c_id_size - 1 := 0;

begin

  s_tready <= (not m_arvalid or m_arready) and
              (not m_rvalid or m_rready);

  data_transfer_i <= s_tvalid and s_tready;

  process (clk)
    variable id_v : std_ulogic_vector(0 to c_id_width - 1);
  begin
    if rising_edge(clk) then
      m_arvalid <= '0';
      if (data_transfer_i = '1') then
        m_arvalid           <= '1';
        m_araddr            <= std_ulogic_vector(resize(unsigned(a), m_araddr'length));
        id_v                := std_ulogic_vector(to_unsigned(id_i, c_id_width));
        m_arid              <= id_v;
        tag_storage_i(id_i) <= s_tag;
        id_i                <= (id_i + 1) mod c_id_size;
      end if;
    end if;
  end process;

  m_rready <= m_tready or (not m_tvalid);

  process (clk)
  begin
    if rising_edge(clk) then
      if sreset = '1' then
        m_tvalid <= '0';
      else
        if m_tready = '1' then
          m_tvalid <= '0';
          if m_rvalid = '1' then
            m_tag    <= tag_storage_i(to_integer(unsigned(m_rid)));
            m_tvalid <= '1';
            m_tdata  <= m_rdata;
          end if;
        end if;
      end if;
    end if;
  end process;

  m_bready <= '1';
  
end architecture rtl;


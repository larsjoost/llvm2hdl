library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_store is
  port (
    clk                       : in  std_ulogic;
    sreset                    : in  std_ulogic;
    s_tvalid                  : in  std_ulogic;
    s_tready                  : out std_ulogic;
    s_taddr                   : in  std_ulogic_vector;
    s_tdata                   : in  std_ulogic_vector;
    s_tag                     : in  std_ulogic_vector;
    m_tag                     : out std_ulogic_vector;
    m_tvalid                  : out std_ulogic;
    m_tready                  : in  std_ulogic;
    m_mem_addr                : out std_ulogic_vector;
    m_mem_addr_id             : out std_ulogic_vector;
    m_mem_addr_valid          : out std_ulogic;
    m_mem_data                : out std_ulogic_vector;
    m_mem_data_valid          : out std_ulogic;
    m_mem_data_ready          : out std_ulogic;
    m_mem_data_response_ready : out std_ulogic;
    s_mem_addr_ready          : in  std_ulogic;
    s_mem_data_ready          : in  std_ulogic;
    s_mem_data_valid          : in  std_ulogic;
    s_mem_data                : in  std_ulogic_vector;
    s_mem_data_id             : in  std_ulogic_vector;
    s_mem_data_response_valid : in  std_ulogic;
    s_mem_data_response_id    : in  std_ulogic_vector
    );
end entity llvm_store;

architecture rtl of llvm_add is

  constant c_id_width : positive := m_mem_addr_id'length;
  constant c_id_size  : positive := 2 ** c_id_width;

  type tag_storage_t is array (0 to c_id_size - 1) of
    std_ulogic_vector(0 to s_tag'length - 1);

  signal tag_storage_i   : tag_storage_t;
  signal data_transfer_i : std_ulogic;
  signal id_i            : natural range 0 to c_id_size - 1 := 0;

begin

  s_tready <= (not m_mem_addr_valid or s_mem_addr_ready) and
              (not m_mem_data_valid or s_mem_data_ready);

  data_transfer_i <= s_tvalid and s_tready;

  process (clk)
  begin
    if rising_edge(clk) then
      if sreset = '1' then
        m_mem_addr_valid <= '0';
        m_mem_data_valid <= '0';
      else
        if s_mem_addr_ready = '1' then
          m_mem_addr_valid <= '0';
        end if;
        if s_mem_data_ready = '1' then
          m_mem_data_valid <= '0';
        end if;
        if (data_transfer_i = '1') then
          m_mem_addr_valid <= '1';
          m_mem_data_valid <= '1';
        end if;
      end if;
    end if;
  end process;

  process (clk)
    variable id_v : memory_id_t;
  begin
    if rising_edge(clk) then
      if (data_transfer_i = '1') then
        m_mem_addr_valid    <= '1';
        m_mem_data_valid    <= '1';
        m_mem_addr          <= memory_addr_t(resize(unsigned(address), m_mem_addr'length));
        id_v                := std_ulogic_vector(to_unsigned(id_i, c_id_width));
        m_mem_addr_id       <= id_v;
        m_mem_data_id       <= id_v;
        m_mem_data          <= memory_data_t(resize(unsigned(data), m_mem_data'length));
        tag_storage_i(id_i) <= tag_in;
        id_i                <= (id_i + 1) mod c_id_size;
      end if;
    end if;
  end process;

  m_mem_data_response_ready <= m_tready or (not m_tvalid);

  process (clk)
  begin
    if rising_edge(clk) then
      if sreset = '1' then
        m_tvalid <= '0';
      else
        if m_ready = '1' then
          m_tvalid <= '0';
        end if;
        if s_mem_data_response_valid = '1' and m_mem_data_response_ready = '1' then
          m_tag    <= tag_storage_i(to_integer(unsigned(s_mem_data_response_id)));
          m_tvalid <= '1';
        end if;
      end if;
    end if;
  end process;

end architecture rtl;

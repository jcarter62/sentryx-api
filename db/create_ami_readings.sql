CREATE TABLE [dbo].[ami_readings](
	[rec_id] [varchar](50) NOT NULL,
	[meter_id] [varchar](25) NOT NULL,
	[reading_dt] [datetime] NOT NULL,
	[reading] [float] NOT NULL,
	[rd_type] [nchar](10) NULL,
	[rd_status] [nchar](10) NULL,
	[rd_unit] [nchar](10) NULL,
	[rd_source] [nchar](10) NULL,
 CONSTRAINT [PK_ami_readings] PRIMARY KEY CLUSTERED
(
	[rec_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];
ALTER TABLE [dbo].[ami_readings] ADD  CONSTRAINT [DF_ami_readings_rec_id]  DEFAULT ([dbo].[shortguid](newid())) FOR [rec_id];

